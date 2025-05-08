from keras.models import load_model
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import joblib
# 모델 불러오기
model = load_model('TSLA_5day.model')
scaler = joblib.load('tsla3_scaler.pkl')
# df = pd.read_excel('TSLA_20190101_20250331.xlsx')
df = pd.read_excel('TSLA_20250207_20250421.xlsx')
test_data = scaler.transform(df['Close'].values.reshape(-1,1))
# 최근데이터
recent_data = test_data[-50:]
x_test = np.reshape(recent_data, (1, recent_data.shape[0], 1))
pred = model.predict(x_test)
pred_inverse = scaler.inverse_transform(pred)
plt.figure(figsize=(20,10))
plt.plot(pred_inverse.flatten(), label='pred')
plt.xlabel('day')
plt.ylabel('price')
plt.legend()
plt.show()
