import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS  # 추가
import pandas as pd
import joblib
import os
import numpy as np
from io import BytesIO
import base64
import json

app = Flask(__name__)
CORS(app)  # CORS 허용 추가

MODEL_PATH = 'prophet_xgb_model_gu.pkl'
ACTUAL_DATA_PATH = "대전2014_2024(구예측).xlsx"

model = None
actual_df = None

def load_model_artifacts():
    global model, actual_df
    if os.path.exists(MODEL_PATH) and os.path.exists(ACTUAL_DATA_PATH):
        model = joblib.load(MODEL_PATH)
        actual_df = pd.read_excel(ACTUAL_DATA_PATH)
        print("✅ 모델 및 실제 데이터 로드 완료!")
        return True
    else:
        print("❌ 모델 또는 실제 데이터 파일이 없습니다. 먼저 학습 코드를 실행해주세요.")
        return False

@app.route('/predict_json', methods=['POST'])
def predict_json():
    if not load_model_artifacts():
        return jsonify({'error': '모델 로딩 실패'}), 500

    try:
        data = request.get_json()
        year_input = int(data.get('year'))
        district_input = data.get('district').strip()

        monthly_predictions = {}
        months = list(range(1, 13))

        prophet_preds_df = pd.read_csv('prophet_predictions_gu.csv')

        for month in months:
            input_data = pd.DataFrame({
                'year': [year_input],
                'month': [month],
                'district': [district_input],
                'prophet_pred': [prophet_preds_df[
                                     (prophet_preds_df['year'] == year_input) & (prophet_preds_df['month'] == month) & (
                                                 prophet_preds_df['district'] == district_input)]['prophet_pred'].values[0]
                                     if not prophet_preds_df[
                    (prophet_preds_df['year'] == year_input) & (prophet_preds_df['month'] == month) & (
                                prophet_preds_df['district'] == district_input)].empty else 0]
            })
            input_data = pd.get_dummies(input_data, columns=['district'])

            model_columns = model.feature_names_in_
            for col in model_columns:
                if col not in input_data.columns:
                    input_data[col] = 0
            input_data = input_data[model_columns]

            prediction = model.predict(input_data)[0]
            monthly_predictions[f'{month}월'] = round(float(prediction), 2)

        return jsonify({
            'district': district_input,
            'year': year_input,
            'monthly_predictions': monthly_predictions
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/', methods=['GET'])
def index():
    return render_template('index_district.html')

@app.route('/result')
def result():
    predictions = request.args.get('predictions')
    district = request.args.get('district')
    year = request.args.get('year')
    monthly_predictions = json.loads(predictions) if predictions else {}
    return render_template( 'result_district.html', monthly_predictions=monthly_predictions, district=district, year=year)

if __name__ == '__main__':
    app.run(debug=True)
