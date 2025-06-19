from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import joblib
from flask_cors import CORS
from sklearn.metrics import mean_absolute_error, mean_squared_error

app = Flask(__name__)
CORS(app)

# 모델 및 데이터 로드
model = joblib.load("district_xgb_model.pkl")
df = pd.read_csv("district_forecast_result.csv")
df.rename(columns={'dong': 'district'}, inplace=True)
df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))


@app.route('/predict_district', methods=['POST'])
def predict_district():
    data = request.get_json()
    district = data.get('district')
    year = int(data.get('year'))

    if district not in df['district'].unique():
        return jsonify({"error": f"'{district}' 구 이름이 데이터에 존재하지 않습니다."}), 400

    filtered = df[(df['district'] == district) & (df['year'] == year)].copy()
    if filtered.empty:
        return jsonify({"error": f"'{district}'의 {year}년도 예측 데이터가 없습니다."}), 404

    filtered = filtered.sort_values(by='month')

    result_df = filtered[['month', 'xgb_pred', 'usage']].copy()
    result_df.rename(columns={'xgb_pred': 'predicted_usage', 'usage': 'actual_usage'}, inplace=True)

    # 소수점 두자리까지만
    result_df['predicted_usage'] = result_df['predicted_usage'].round(2)
    result_df['actual_usage'] = result_df['actual_usage'].round(2)

    # 월 누락 보완
    full_months = pd.DataFrame({'month': range(1, 13)})
    result_df = pd.merge(full_months, result_df, on='month', how='left')
    result_df['district'] = district
    result_df['year'] = year
    result_df = result_df.replace({np.nan: None})

    response = {
        "district": district,
        "year": year,
        "results": result_df.to_dict(orient='records')
    }

    if result_df['actual_usage'].notna().sum() > 0:
        valid = result_df.dropna(subset=['actual_usage'])
        y_true = valid['actual_usage']
        y_pred = valid['predicted_usage']

        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        similarity = 100 - mape

        response["metrics"] = {
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "mape": round(mape, 2),
            "similarity": round(similarity, 2)
        }

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
