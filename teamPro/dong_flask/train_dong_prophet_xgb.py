import pandas as pd
import numpy as np
from prophet import Prophet
from tqdm import tqdm
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
import joblib

# [1] 데이터 불러오기
df = pd.read_excel("동별세대당전기요금.xlsx")

# [2] Prophet 예측값 생성
prophet_preds = pd.DataFrame()
dong_list = df['dong'].unique()

print("📊 Prophet 예측 시작...")

for dong in tqdm(dong_list):
    df_dong = df[df['dong'] == dong][['year', 'month', 'final_monthly_fee']].copy()
    df_dong['ds'] = pd.to_datetime(df_dong[['year', 'month']].assign(day=1))
    df_dong['y'] = df_dong['final_monthly_fee']

    prophet = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
    prophet.fit(df_dong[['ds', 'y']])

    future = prophet.make_future_dataframe(periods=12, freq='MS')
    forecast = prophet.predict(future)

    forecast_result = forecast[['ds', 'yhat']].copy()
    forecast_result['dong'] = dong
    forecast_result['year'] = forecast_result['ds'].dt.year
    forecast_result['month'] = forecast_result['ds'].dt.month
    forecast_result.rename(columns={'yhat': 'prophet_pred'}, inplace=True)

    prophet_preds = pd.concat([prophet_preds, forecast_result[['dong', 'year', 'month', 'prophet_pred']]])

print("✅ Prophet 예측 완료")

# [3] 예측 결과 저장 (선택)
prophet_preds.to_csv("prophet_predictions.csv", index=False)

# [4] Prophet 결과를 원본 데이터와 병합
df_all = df.merge(prophet_preds, on=["dong", "year", "month"], how="left")

# [5] XGBoost 학습
features = df_all[['dong', 'year', 'month', 'prophet_pred']].copy()
features = pd.get_dummies(features, columns=['dong'])
target = df_all['final_monthly_fee']

X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

xgb_model = XGBRegressor(n_estimators=300, learning_rate=0.1, random_state=42)
xgb_model.fit(X_train, y_train)

# [6] XGBoost 모델 저장
joblib.dump(xgb_model, '../prophet_xgb_model.pkl')
print("✅ XGBoost 모델 저장 완료: prophet_xgb_model.pkl")
