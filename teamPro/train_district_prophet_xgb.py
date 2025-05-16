import pandas as pd
import numpy as np
from prophet import Prophet
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
import joblib
from tqdm import tqdm
import os

# [1] 데이터 불러오기
df = pd.read_excel("대전_전력사용량_2014_2024.xlsx")

# [2] 컬럼명 정리 및 파생
df.columns = df.columns.str.strip()
df.rename(columns={"동": "dong", "전력사용량": "usage"}, inplace=True)
df['year'] = df['DATE'].dt.year
df['month'] = df['DATE'].dt.month

# [3] Prophet 예측 수행
prophet_preds = pd.DataFrame()
dong_list = df['dong'].unique()

print("📊 Prophet 예측 시작...")
for dong in tqdm(dong_list):
    df_dong = df[df['dong'] == dong][['DATE', 'usage']].copy()
    df_dong.rename(columns={'DATE': 'ds', 'usage': 'y'}, inplace=True)

    model = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
    model.fit(df_dong)

    future = model.make_future_dataframe(periods=12, freq='MS')
    forecast = model.predict(future)

    forecast_result = forecast[['ds', 'yhat']].copy()
    forecast_result['dong'] = dong
    forecast_result['year'] = forecast_result['ds'].dt.year
    forecast_result['month'] = forecast_result['ds'].dt.month
    forecast_result.rename(columns={'yhat': 'prophet_pred'}, inplace=True)

    prophet_preds = pd.concat([prophet_preds, forecast_result[['dong', 'year', 'month', 'prophet_pred']]])

print("✅ Prophet 예측 완료")

# [4] Prophet 결과 병합
df_all = df.merge(prophet_preds, on=["dong", "year", "month"], how="left")

# [5] XGBoost 학습 준비
features = df_all[['dong', 'year', 'month', 'prophet_pred']].copy()
features = pd.get_dummies(features, columns=['dong'])
target = df_all['usage']

X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

# [6] XGBoost 학습
print("📈 XGBoost 학습 시작...")
xgb_model = XGBRegressor(n_estimators=300, learning_rate=0.1, random_state=42)
xgb_model.fit(X_train, y_train)
print("✅ XGBoost 학습 완료")

# [7] 모델 저장
joblib.dump(xgb_model, "daejeon_xgb_model.pkl")
print("💾 모델 저장 완료: daejeon_xgb_model.pkl")

# [8] 예측 결과 저장
df_all['xgb_pred'] = xgb_model.predict(features)
df_all.to_csv("daejeon_forecast_result.csv", index=False)
print("📁 결과 저장 완료: daejeon_forecast_result.csv")
