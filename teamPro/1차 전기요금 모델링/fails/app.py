from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import os

# Flask 앱 초기화
app = Flask(__name__)
CORS(app)

# 모델 및 칼럼 로딩
MODEL_PATH = "xgb_models/xgb_model.pkl"
COL_PATH = "xgb_models/xgb_model_columns.pkl"
DATA_PATH = "동별세대당전기요금.xlsx"

# 모델과 feature columns 로딩
model = joblib.load(MODEL_PATH)
with open(COL_PATH, "rb") as f:
    model_columns = joblib.load(f)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    dong = data.get("dong", "").strip()
    year = data.get("year", "")

    # 유효성 검사
    if not dong or not str(year).isdigit():
        return jsonify({'error': 'dong과 year는 필수이며 year는 숫자여야 합니다.'}), 400

    year = int(year)

    # 예측용 input 생성
    input_rows = [{"dong": dong, "year": year, "month": m} for m in range(1, 13)]
    input_df = pd.DataFrame(input_rows)
    input_df = pd.get_dummies(input_df)

    # 누락된 칼럼 보정
    for col in model_columns:
        if col not in input_df.columns:
            input_df[col] = 0
    input_df = input_df[model_columns]

    # 예측
    y_pred = model.predict(input_df).round().astype(int)

    # 결과 저장
    result = {
        "dong": dong,
        "year": year,
        "predictions": [{"month": m, "predicted_fee": int(y)} for m, y in zip(range(1, 13), y_pred)]
    }

    # 실제값 비교 (있으면)
    if os.path.exists(DATA_PATH):
        df_real = pd.read_excel(DATA_PATH)
        df_real = df_real[(df_real["dong"] == dong) & (df_real["year"] == year)]
        if not df_real.empty:
            real_dict = df_real.set_index("month")["final_monthly_fee"].to_dict()
            for row in result["predictions"]:
                month = row["month"]
                if month in real_dict:
                    actual = real_dict[month]
                    pred = row["predicted_fee"]
                    row["actual_fee"] = int(actual)
                    row["error"] = abs(pred - actual)
                    row["similarity(%)"] = round((1 - abs(pred - actual) / actual) * 100, 2)

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
