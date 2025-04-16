import pandas as pd
import re
import numpy as np
import os
import pickle
from konlpy.tag import Okt
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model

data_dir = 'naver_data'
max_len = 100
# 불용어
stopwords = ['은', '는', '의', '가', '아', '좀', '잘', '강', '를']
okt = Okt()
# 토크나이저 가져오기
with open(f"{data_dir}/tokenizer.pkl", 'rb') as f:
    tokenizer = pickle.load(f)
# 모델
model = load_model('best_lstm_model.h5')
def preprocess_text(text):
    text = re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣]','',text) # 한글과 공백 빼고 제외
    tokens = okt.morphs(text, stem=True)
    tokens = [word for word in tokens if word not in stopwords]
    seq = tokenizer.texts_to_sequences(tokens)
    padded = pad_sequences(seq, maxlen=max_len)
    return padded
# 예측 함수
def predict(sentence):
    input_data = preprocess_text(sentence)
    pred = float(model.predict(input_data)[0])
    print("\n 사용자 입력:", sentence)
    print("LSTM 기본 모델")
    print(" -> 긍정" if pred > 0.5 else " -> 부정", f"({pred:.2%})")
if __name__ == '__main__':
    while True:
        user_input = input("\n 감성 분석 문장을 입력하세요!(종료:q): ")
        if user_input == "q":
            break
        predict(user_input)


