from ultralytics import YOLO
from flask import Flask, render_template, request, jsonify
import cv2
import os
from werkzeug.utils import secure_filename
import base64
import re
import numpy as np
app = Flask(__name__)
model = YOLO('yolov8n.pt')

@app.route("/")
def index():
    return render_template("yolo_video.html")
@app.route("/analyze_frame", methods=["POST"])
def analyze():
    data_url = request.form['image']
    # base64 인코딩 포맷에서 base64 데이터만 추출
    image_data = re.sub('^data:image/.+;base64','',data_url)
    # 이미지로 변환하여 출력
    image = np.frombuffer(base64.b64decode(image_data), np.uint8)
    frame = cv2.imdecode(image, cv2.IMREAD_COLOR)
    frame = cv2.resize(frame, (320, 320))
    results = model(frame)
    annotated_frame = results[0].plot(show=False)
    # 결과를 다시 base64로
    _, buffer = cv2.imencode(".jpg", annotated_frame)
    result_image = base64.b64encode(buffer).decode("utf-8")
    result_url = 'data:image/jpeg;base64,'+result_image
    return jsonify({'result_image':result_url})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")


