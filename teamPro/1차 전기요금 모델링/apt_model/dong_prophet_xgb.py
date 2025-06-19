import pandas as pd
import numpy as np
from prophet import Prophet
from xgboost import XGBRegressor
import joblib
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error

# [0] 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# [1] 데이터 불러오기 및 모델 로드
df = pd.read_excel("동별세대당전기요금.xlsx")
model = joblib.load("prophet_xgb_model.pkl")

# [2] 사용자 입력
dong_input = input("예측할 동 이름을 입력하세요 (예: 둔산동): ")
year_input = int(input("예측할 연도를 입력하세요 (예: 2024): "))

# [3] Prophet 예측 생성
df_dong = df[df['dong'] == dong_input][['year', 'month', 'final_monthly_fee']].copy()
df_dong['ds'] = pd.to_datetime(df_dong[['year', 'month']].assign(day=1))
df_dong['y'] = df_dong['final_monthly_fee']

prophet = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
prophet.fit(df_dong[['ds', 'y']])
future = prophet.make_future_dataframe(periods=12, freq='MS')
forecast = prophet.predict(future)

forecast['dong'] = dong_input
forecast['year'] = forecast['ds'].dt.year
forecast['month'] = forecast['ds'].dt.month
forecast.rename(columns={'yhat': 'prophet_pred'}, inplace=True)

# [4] 타겟 연도 예측값 필터링
target_year_data = forecast[forecast['year'] == year_input][['dong', 'year', 'month', 'prophet_pred']]

# [5] XGBoost feature 구성
features = target_year_data.copy()
features = pd.get_dummies(features, columns=['dong'])
trained_features = model.get_booster().feature_names
for col in trained_features:
    if col not in features.columns:
        features[col] = 0
features = features[trained_features]

# [6] XGBoost 예측 수행
xgb_pred = model.predict(features)

# [7] 결과 통합
result_df = target_year_data[['month']].copy()
result_df['xgb_pred'] = np.round(xgb_pred)

# [8] 실제값 병합
real_data = df[(df['dong'] == dong_input) & (df['year'] == year_input)]
if not real_data.empty:
    result_df = pd.merge(result_df, real_data[['month', 'final_monthly_fee']], on='month', how='left')
    result_df.rename(columns={'final_monthly_fee': 'real_fee'}, inplace=True)
else:
    result_df['real_fee'] = np.nan

# [9] 유사도 출력 (실제값이 일부라도 존재할 경우만)
if result_df['real_fee'].notna().sum() > 0:
    valid = result_df.dropna(subset=['real_fee'])
    y_true = valid['real_fee']
    y_pred = valid['xgb_pred']

    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100

    print("\n📈 XGBoost 예측 vs 실제값 유사도")
    print(f"▶ MAE  : {mae:.2f} 원")
    print(f"▶ RMSE : {rmse:.2f} 원")
    print(f"▶ MAPE : {mape:.2f} %")
else:
    print("\n⚠️ 선택한 연도에는 실제 요금 데이터가 없어 유사도 계산은 생략합니다.")

# [10] 결과 출력
print(f"\n📊 {year_input}년 '{dong_input}' 월별 전기요금 예측 결과")
print(result_df.rename(columns={
    'month': '월',
    'xgb_pred': 'XGBoost 예측',
    'real_fee': '실제 요금'
}).to_string(index=False))

# [11] 시각화
plt.figure(figsize=(10, 5))
plt.plot(result_df['month'], result_df['xgb_pred'], marker='o', label='XGBoost 예측', linestyle='-')
if result_df['real_fee'].notna().any():
    plt.plot(result_df['month'], result_df['real_fee'], marker='o', label='실제 요금', linestyle=':')

plt.title(f"{year_input}년 '{dong_input}' 월별 전기요금 비교")
plt.xlabel("월")
plt.ylabel("요금 (원)")
plt.xticks(result_df['month'])
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend()
plt.tight_layout()
plt.show()
