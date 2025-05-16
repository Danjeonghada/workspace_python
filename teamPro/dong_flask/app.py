from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import joblib
from prophet import Prophet
from flask_cors import CORS
from sklearn.metrics import mean_absolute_error, mean_squared_error

app = Flask(__name__)
CORS(app)

# 모델 & 데이터 불러오기 (초기화 시 1회만)
model = joblib.load("prophet_xgb_model.pkl")
df = pd.read_excel("동별세대당전기요금.xlsx")


@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    dong = data['dong']
    year = int(data['year'])

    if dong not in df['dong'].unique():
        return jsonify({"error": "해당 동 이름이 존재하지 않습니다."}), 400

    # [1] Prophet 예측 준비
    df_dong = df[df['dong'] == dong][['year', 'month', 'final_monthly_fee']].copy()
    df_dong['ds'] = pd.to_datetime(df_dong[['year', 'month']].assign(day=1))
    df_dong['y'] = df_dong['final_monthly_fee']

    prophet = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
    prophet.fit(df_dong[['ds', 'y']])
    future = prophet.make_future_dataframe(periods=24, freq='MS')  # 넉넉히 생성
    forecast = prophet.predict(future)

    forecast['dong'] = dong
    forecast['year'] = forecast['ds'].dt.year
    forecast['month'] = forecast['ds'].dt.month
    forecast.rename(columns={'yhat': 'prophet_pred'}, inplace=True)

    # [2] 해당 연도 예측 데이터 추출
    target_year_data = forecast[forecast['year'] == year][['dong', 'year', 'month', 'prophet_pred']]

    # [3] XGBoost 예측
    features = target_year_data.copy()
    features = pd.get_dummies(features, columns=['dong'])

    trained_features = model.get_booster().feature_names
    for col in trained_features:
        if col not in features.columns:
            features[col] = 0
    features = features[trained_features]

    xgb_pred = model.predict(features)

    result_df = target_year_data[['month']].copy()
    result_df['xgb_pred'] = np.round(xgb_pred)

    # [4] 실제값 병합
    real_data = df[(df['dong'] == dong) & (df['year'] == year)]
    if not real_data.empty:
        result_df = pd.merge(result_df, real_data[['month', 'final_monthly_fee']], on='month', how='left')
        result_df.rename(columns={'final_monthly_fee': 'real_fee'}, inplace=True)
    else:
        result_df['real_fee'] = np.nan

    # [5] 월 누락 방지 (1~12월 보장)
    full_months = pd.DataFrame({'month': range(1, 13)})
    result_df = pd.merge(full_months, result_df, on='month', how='left')
    result_df['dong'] = dong
    result_df['year'] = year

    # [6] NaN → None
    result_df = result_df.replace({np.nan: None})
    result = result_df.to_dict(orient='records')

    # [7] 응답 구성
    response = {
        "dong": dong,
        "year": year,
        "results": result
    }

    # [8] 정확도 메트릭 계산 (실제값 일부라도 있을 경우)
    if result_df['real_fee'].notna().sum() > 0:
        valid = result_df.dropna(subset=['real_fee'])
        y_true = valid['real_fee']
        y_pred = valid['xgb_pred']

        mae = mean_absolute_error(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100

        response["metrics"] = {
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "mape": round(mape, 2)
        }

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
