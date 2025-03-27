from flask import Flask, request, jsonify, render_template
import pickle
import numpy as np

app = Flask(__name__)
# 모델 로드
with open('coffee_model.pk1', 'rb') as f:
    model = pickle.load(f)

@app.route("/")
def home():
    return render_template('index.html')
@app.route("/predict", methods=['POST'])
def predict():
    print(request.form)
    temperature = float(request.form['temperature'])
    humidity = float(request.form['humidity'])
    precipitation = float(request.form['precipitation'])
    input_data = np.array([[temperature, humidity, precipitation]])
    pred = model.predict(input_data)
    print(pred)
    # 예측 결과를 딕셔너리 형태로 정리
    result = {
        'iced_ame':float(pred[0][0])
       ,'hot_ame':float(pred[0][1])
       ,'shaved_ice':float(pred[0][4])
    }
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)