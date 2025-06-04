import pandas as pd
import numpy as np
from prophet import Prophet
from tqdm import tqdm
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt

# [0] 한글 폰트 설정 (Windows 환경)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# [1] 데이터 불러오기
df = pd.read_excel("대전2014_2024(구예측).xlsx")

# [2] Prophet 예측값 생성 (구별)
prophet_preds_gu = pd.DataFrame()
gu_list = df['district'].unique()

print("📊 Prophet (구별) 예측 시작...")

for gu in tqdm(gu_list):
    df_gu = df[df['district'] == gu][['year', 'month', 'powerUsage']].copy()
    df_gu['ds'] = pd.to_datetime(df_gu[['year', 'month']].assign(day=1))
    df_gu['y'] = df_gu['powerUsage']

    prophet = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
    prophet.fit(df_gu[['ds', 'y']])

    future = prophet.make_future_dataframe(periods=12, freq='MS')
    forecast = prophet.predict(future)

    forecast_result = forecast[['ds', 'yhat']].copy()
    forecast_result['district'] = gu
    forecast_result['year'] = forecast_result['ds'].dt.year
    forecast_result['month'] = forecast_result['ds'].dt.month
    forecast_result.rename(columns={'yhat': 'prophet_pred'}, inplace=True)

    prophet_preds_gu = pd.concat([prophet_preds_gu, forecast_result[['district', 'year', 'month', 'prophet_pred']]])

print("✅ Prophet (구별) 예측 완료")

# [3] 예측 결과 저장 (선택)
prophet_preds_gu.to_csv("prophet_predictions_gu.csv", index=False)

# [4] Prophet 결과를 원본 데이터와 병합
df_all_gu = df.merge(prophet_preds_gu, on=["district", "year", "month"], how="left")

# [5] XGBoost 학습 (구별)
features_gu = df_all_gu[['district', 'year', 'month', 'prophet_pred']].copy()
features_gu = pd.get_dummies(features_gu, columns=['district'])
target_gu = df_all_gu['powerUsage']

X_train_gu, X_test_gu, y_train_gu, y_test_gu = train_test_split(features_gu, target_gu, test_size=0.2, random_state=42)

xgb_model_gu = XGBRegressor(n_estimators=300, learning_rate=0.1, random_state=42)
xgb_model_gu.fit(X_train_gu, y_train_gu)

# [6] XGBoost 모델 저장
joblib.dump(xgb_model_gu, 'prophet_xgb_model_gu.pkl')
print("✅ XGBoost (구별) 모델 저장 완료: prophet_xgb_model_gu.pkl")

# [7] (선택 사항) 모델 성능 평가
y_pred_gu = xgb_model_gu.predict(X_test_gu)
mae_gu = mean_absolute_error(y_test_gu, y_pred_gu)
rmse_gu = np.sqrt(mean_squared_error(y_test_gu, y_pred_gu))
print(f"📌 XGBoodst (구별) Test MAE: {mae_gu:.2f}")
print(f"📌 XGBoost (구별) Test RMSE: {rmse_gu:.2f}")

# [8] (선택 사항) 예측 결과 시각화 (테스트 데이터 일부)
comparison_gu_df = pd.DataFrame({'실제': y_test_gu, '예측': y_pred_gu})
plt.figure(figsize=(10, 6))
plt.scatter(comparison_gu_df.index, comparison_gu_df['실제'], label='실제 전력 사용량', alpha=0.6)
plt.scatter(comparison_gu_df.index, comparison_gu_df['예측'], label='예측 전력 사용량', alpha=0.6)
plt.xlabel('데이터 포인트')
plt.ylabel('전력 사용량')
plt.title('실제 vs 예측 전력 사용량 (구별 모델 - 테스트 데이터 일부)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

print("\n✅ '구'별 전력 사용량 예측 모델 생성 완료 및 저장.")
print("✅ 이제 'prophet_xgb_model_gu.pkl' 파일을 사용하여 예측을 수행할 수 있습니다.")