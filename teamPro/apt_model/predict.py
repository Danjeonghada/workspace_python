import pandas as pd
import pickle
import numpy as np
dir = "model"
# 1. 저장된 모델, 스케일러, 컬럼 로드
with open(f"{dir}/model.pkl", "rb") as f:
    model = pickle.load(f)

with open(f"{dir}/scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

with open(f"{dir}/columns.pkl", "rb") as f:
    columns = pickle.load(f)

# 2. 사용자 입력 받기
dong_input = input("동 이름을 입력하세요 (예: 중촌동): ").strip()
year_input = int(input("연도를 입력하세요 (예: 2026): "))


# 3. 입력값 생성 (year는 숫자, dong은 원핫 인코딩)
input_dict = {col: 0 for col in columns}
input_dict["year"] = year_input  # ✅ year는 수치형 그대로 사용

dong_col = f"dong_{dong_input}"
if dong_col in input_dict:
    input_dict[dong_col] = 1
else:
    print(f"⚠️ 지원하지 않는 동 이름: {dong_input}")
    exit()

# 4. 스케일링 및 예측
input_df = pd.DataFrame([input_dict])
input_scaled = scaler.transform(input_df)
pred = model.predict(input_scaled)[0]

print(f"📈 예측된 '{dong_input}'의 {year_input}년 다가구주택 수는 약 {round(pred, 2)}세대입니다.")