import pandas as pd
from prophet import Prophet
import joblib
import os

# 1. 저장할 폴더 만들기
os.makedirs("saved_models", exist_ok=True)

# 2. 엑셀 파일 불러오기
df = pd.read_excel("동별세대당전기요금.xlsx")

df = df[df["year"] <= 2023]

# 3. 동 리스트 추출
dong_list = df["dong"].unique()

# 4. 동별 Prophet 모델 학습 및 저장
for dong in dong_list:
    dong_df = df[df["dong"] == dong].copy()
    dong_df["ds"] = pd.to_datetime(dong_df["year"].astype(str) + "-" + dong_df["month"].astype(str) + "-01")
    dong_df = dong_df[["ds", "final_monthly_fee"]].rename(columns={"final_monthly_fee": "y"})

    if len(dong_df) < 12:
        print(f"[스킵] {dong} → 데이터가 12개월 미만입니다.")
        continue

    model = Prophet()
    model.fit(dong_df)

    # 모델 저장
    model_path = f"saved_models/{dong}_model.pkl"
    joblib.dump(model, model_path)
    print(f"[저장 완료] {dong} → {model_path}")

print("\n✅ 모든 모델 저장 완료")
