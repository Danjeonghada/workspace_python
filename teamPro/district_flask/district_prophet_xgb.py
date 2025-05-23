import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error

# [0] 폰트 설정 (한글 그래프용)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# [1] 데이터 및 모델 로드
df = pd.read_csv("district_forecast_result.csv")
df.rename(columns={'dong': 'district'}, inplace=True)  # 통일

# [2] 사용자 입력
district_input = input("예측할 구 이름을 입력하세요 (예: 유성구): ").strip()
year_input = int(input("예측할 연도를 입력하세요 (예: 2025): "))

# [3] 날짜 열 생성
df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))

# [4] 필터링
filtered = df[(df['district'] == district_input) & (df['year'] == year_input)].copy()
if filtered.empty:
    print(f"\n⚠️ {district_input}의 {year_input}년도 데이터가 없습니다.")
    exit()

# [5] 시계열 정렬
filtered = filtered.sort_values(by='month')

# [6] 평가 지표 (실제값 있는 경우만)
if filtered['usage'].notna().sum() > 0:
    valid = filtered.dropna(subset=['usage'])
    mae = mean_absolute_error(valid['usage'], valid['xgb_pred'])
    rmse = np.sqrt(mean_squared_error(valid['usage'], valid['xgb_pred']))
    mape = np.mean(np.abs((valid['usage'] - valid['xgb_pred']) / valid['usage'])) * 100

    print("\n📈 예측 정확도 (XGBoost vs 실제 사용량)")
    print(f"▶ MAE   : {mae:,.2f} kWh")
    print(f"▶ RMSE  : {rmse:,.2f} kWh")
    print(f"▶ MAPE  : {mape:.2f} %")
else:
    print("\n⚠️ 해당 연도에 실제 사용량 데이터가 없어 정확도 평가는 생략합니다.")

# [7] 결과 표 출력
result_table = filtered[['month', 'xgb_pred', 'usage']].rename(columns={
    'month': '월',
    'xgb_pred': '예측 사용량',
    'usage': '실제 사용량'
}).fillna('-')

print(f"\n📊 {year_input}년 '{district_input}' 월별 전력 사용량 예측")
print(result_table.to_string(index=False))

# [8] 시각화
plt.figure(figsize=(10, 5))
plt.plot(filtered['month'], filtered['xgb_pred'], marker='o', linewidth=2.5, label='XGBoost 예측', color='steelblue')

if filtered['usage'].notna().any():
    plt.plot(filtered['month'], filtered['usage'], marker='s', linewidth=2.0, linestyle='--', label='실제 사용량', color='orange')

plt.title(f"{year_input}년 '{district_input}' 월별 전력 사용량 비교", fontsize=14)
plt.xlabel("월")
plt.ylabel("전력 사용량 (kWh)")
plt.xticks(filtered['month'])
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.tight_layout()
plt.show()
