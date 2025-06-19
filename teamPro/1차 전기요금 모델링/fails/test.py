import pandas as pd
import joblib
import os

# 모델 경로
MODEL_PATH = "xgb_models/xgb_model.pkl"
COL_PATH = "xgb_models/xgb_model_columns.pkl"

# 모델 로드
model = joblib.load(MODEL_PATH)
with open(COL_PATH, "rb") as f:
    model_columns = joblib.load(f)

# 테스트할 동 (존재하는 동 이름으로 변경 가능)
dong_name = "장대동"

# 테스트할 연도 목록
test_years = [2024, 2025]

# 결과 저장용
results = {}

for year in test_years:
    # 입력 데이터 구성
    input_rows = [{"dong": dong_name, "year": year, "month": m} for m in range(1, 13)]
    input_df = pd.DataFrame(input_rows)

    # 원-핫 인코딩
    input_df = pd.get_dummies(input_df)

    # 누락된 칼럼 보정
    for col in model_columns:
        if col not in input_df.columns:
            input_df[col] = 0
    input_df = input_df[model_columns]

    # 예측
    y_pred = model.predict(input_df).round().astype(int)
    results[year] = list(y_pred)

# 예측 결과 비교 출력
for year in test_years:
    print(f"\n📅 {year}년 예측:")
    print(results[year])

# 추가 비교: 값이 동일한지 판단
print("\n🔍 모든 연도 예측값이 동일한가?")
first = results[test_years[0]]
all_same = all(results[y] == first for y in test_years[1:])
print("✅ 동일함" if all_same else "❌ 다름")
