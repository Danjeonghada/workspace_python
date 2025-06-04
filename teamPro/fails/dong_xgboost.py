import pandas as pd
import joblib
import os
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

# 1. 모델 로드
model_path = "dong_flask/xgb_models/xgb_model.pkl"
if not os.path.exists(model_path):
    print("❌ 학습된 모델이 존재하지 않습니다. 먼저 train_xgboost.py를 실행하세요.")
    exit()

model = joblib.load(model_path)

# 2. 사용자 입력
dong = input("동 입력 (예: 둔산동): ").strip()
year = int(input("예측할 연도 입력 (예: 2025): ").strip())

# 3. 1~12월 예측용 데이터프레임 생성
input_df = pd.DataFrame([{"dong": dong, "year": year, "month": m} for m in range(1, 13)])
input_df = pd.get_dummies(input_df)

# 4. 누락된 컬럼 보정
model_features = model.get_booster().feature_names
for col in model_features:
    if col not in input_df.columns:
        input_df[col] = 0
input_df = input_df[model_features]

# 5. 예측 수행
y_pred = model.predict(input_df).round().astype(int)

# 6. 예측 결과 정리
result_df = pd.DataFrame({
    "월": range(1, 13),
    "예측 전기요금": y_pred
})

# 7. 실제값 불러와 비교 (있을 경우)
real_path = "동별세대당전기요금.xlsx"
if os.path.exists(real_path):
    df_real = pd.read_excel(real_path)
    df_real = df_real[(df_real["dong"] == dong) & (df_real["year"] == year)]
    df_real = df_real[["month", "final_monthly_fee"]].rename(columns={"month": "월"})
    compare = pd.merge(result_df, df_real, on="월", how="left")

    if not compare["final_monthly_fee"].isnull().all():
        compare["절대 오차"] = (compare["예측 전기요금"] - compare["final_monthly_fee"]).abs()
        compare["유사도(%)"] = (1 - compare["절대 오차"] / compare["final_monthly_fee"]) * 100
        compare["유사도(%)"] = compare["유사도(%)"].round(2)

        # 평균 정확도
        filtered = compare.dropna(subset=["유사도(%)"])
        mae = mean_absolute_error(filtered["final_monthly_fee"], filtered["예측 전기요금"])
        rmse = np.sqrt(mean_squared_error(filtered["final_monthly_fee"], filtered["예측 전기요금"]))
        mean_sim = filtered["유사도(%)"].mean().round(2)

        print(f"\n📊 {dong} {year}년 예측 결과 (XGBoost)")
        print(compare)
        print(f"\n✅ 평균 유사도: {mean_sim}%")
        print(f"✅ MAE: {mae:.2f} 원 | RMSE: {rmse:.2f} 원")
        # 그래프 출력 (예측 vs 실제)
        import matplotlib.pyplot as plt

        plt.rcParams["font.family"] = "Malgun Gothic"
        plt.rcParams["axes.unicode_minus"] = False

        plt.figure(figsize=(10, 5))
        plt.plot(compare["월"], compare["예측 전기요금"], label="예측 전기요금", marker="o")
        plt.plot(compare["월"], compare["final_monthly_fee"], label="실제 전기요금", marker="x")
        plt.title(f"{dong} {year}년 월별 전기요금 예측 vs 실제 (XGBoost)")
        plt.xlabel("월")
        plt.ylabel("전기요금 (원)")
        plt.legend()
        plt.grid(True)
        plt.xticks(range(1, 13))
        plt.tight_layout()
        plt.show()
    else:
        print(f"\n📊 {dong} {year}년 예측 결과 (실제값 없음)")
        print(result_df)
else:
    print(f"\n📊 {dong} {year}년 예측 결과 (실제 데이터 파일 없음)")
    print(result_df)
