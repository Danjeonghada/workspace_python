import pandas as pd
import numpy as np
from prophet import Prophet
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error

# [1] 데이터 불러오기
df = pd.read_excel("동별세대당전기요금.xlsx")

# [2] Prophet 예측값 생성 (동별)
prophet_preds = pd.DataFrame()
dong_list = df['dong'].unique()

print("📊 Prophet 예측 시작...")

for dong in dong_list:
    df_dong = df[df['dong'] == dong][['year', 'month', 'final_monthly_fee']].copy()
    df_dong['ds'] = pd.to_datetime(df_dong[['year', 'month']].assign(day=1))
    df_dong['y'] = df_dong['final_monthly_fee']

    model = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
    model.fit(df_dong[['ds', 'y']])

    future = model.make_future_dataframe(periods=12, freq='MS')  # 12개월 예측
    forecast = model.predict(future)

    forecast['dong'] = dong
    forecast['year'] = forecast['ds'].dt.year
    forecast['month'] = forecast['ds'].dt.month
    forecast.rename(columns={'yhat': 'prophet_pred'}, inplace=True)

    prophet_preds = pd.concat([prophet_preds, forecast[['dong', 'year', 'month', 'prophet_pred']]])

print("✅ Prophet 예측 완료")

# [3] Prophet 예측값 병합
df_all = df.merge(prophet_preds, on=["dong", "year", "month"], how="left")

# [4] XGBoost 학습 준비
features = df_all[['dong', 'year', 'month', 'prophet_pred']].copy()
features = pd.get_dummies(features, columns=['dong'])  # 동을 one-hot 인코딩
target = df_all['final_monthly_fee']

# [5] 학습/테스트 분리 및 모델 학습
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

model = XGBRegressor(n_estimators=300, learning_rate=0.1, random_state=42)
model.fit(X_train, y_train)

# [6] 예측 및 평가
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print("\n📈 [Prophet + XGBoost] 예측 성능")
print(f"▶ MAE  : {mae:.2f} 원")
print(f"▶ RMSE : {rmse:.2f} 원")

# [선택] 모델 저장
# import joblib
# joblib.dump(model, 'prophet_xgb_model.pkl')
