import pandas as pd
from prophet import Prophet
import joblib
import matplotlib.pyplot as plt


plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

# 사용자 입력
dong = input("동 입력 (예: 둔산동): ").strip()
target_year = int(input("예측할 연도 입력 (예: 2025): ").strip())

# 1. Prophet 모델 로드
model_path = f"saved_models/{dong}_model.pkl"
model = joblib.load(model_path)

# 2. 예측할 연도 12개월 날짜 생성
date_range = pd.date_range(start=f"{target_year}-01-01", periods=12, freq="MS")
future_df = pd.DataFrame({"ds": date_range})

# 3. 예측 수행
forecast = model.predict(future_df)
forecast["yhat"] = forecast["yhat"].round().astype(int)
forecast = forecast[["ds", "yhat"]]

# 4. 실제값 불러오기
df_real = pd.read_excel("동별세대당전기요금.xlsx")
df_real = df_real[(df_real["dong"] == dong) & (df_real["year"] == target_year)]
df_real["ds"] = pd.to_datetime(df_real["year"].astype(str) + "-" + df_real["month"].astype(str) + "-01")
df_real = df_real[["ds", "final_monthly_fee"]]

# 5. 시각화
plt.figure(figsize=(10, 5))
plt.plot(forecast["ds"], forecast["yhat"], label="예측 전기요금", marker="o")

if not df_real.empty:
    plt.plot(df_real["ds"], df_real["final_monthly_fee"], label="실제 전기요금", marker="x")

plt.title(f"{dong} {target_year}년 월별 세대당 전기요금 예측 vs 실제")
plt.xlabel("월")
plt.ylabel("전기요금 (원)")
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

if not df_real.empty:
    import numpy as np

    compare = pd.merge(forecast, df_real, on="ds", how="inner")
    compare["월"] = compare["ds"].dt.month
    compare["절대 오차"] = abs(compare["yhat"] - compare["final_monthly_fee"])
    compare["유사도(%)"] = (1 - compare["절대 오차"] / compare["final_monthly_fee"]) * 100
    compare["유사도(%)"] = compare["유사도(%)"].round(2)

    print(f"\n📊 {dong} {target_year}년 월별 유사도 분석")
    print(compare[["월", "final_monthly_fee", "yhat", "절대 오차", "유사도(%)"]])

else:
    print("\n⚠ 실제값이 없어 유사도 분석을 생략합니다.")
