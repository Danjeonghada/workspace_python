import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout, BatchNormalization
from keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler
import joblib

# 데이터 로드
df = pd.read_excel('TSLA_20190101_20250331.xlsx')

# 정규화 기법 중 하나로 데이터를 지정한 범위 (0, 1) 0 ~ 1 사이 범위로 변환
# 정규화 하는 이유는 수렴 속도 향상, 큰 값의 영향력 감소 (안정됨)
scaler = MinMaxScaler(feature_range=(0,1))
df['Close'] = scaler.fit_transform((df['Close'].values.reshape(-1,1)))
joblib.dump(scaler, 'tsla2_scaler.pkl') # 저장 (복원을 위해)

# 시계열 데이터 생성
def create_sequences(p_data, seq_length, size):
    result = []
    for i in range(len(p_data) - seq_length - size + 1):
        result.append(p_data[i:i + seq_length + size])
    return np.array(result)

x_size = 50
y_size = 1
dataset = create_sequences(df['Close'].values, x_size, y_size)
print(dataset.shape)

# 학습/테스트 분할
train_size = int(len(dataset) * 0.9)
train_data = dataset[:train_size]
test_data = dataset[train_size:]

x_train = train_data[:, :-y_size]
y_train = train_data[:, -y_size:]
x_test = test_data[:, :-y_size]
y_test = test_data[:, -y_size:]

# reshape
x_train = x_train.reshape((x_train.shape[0], x_train.shape[1], 1))
x_test = x_test.reshape((x_test.shape[0], x_test.shape[1], 1))

# 모델 구성
model = Sequential()
model.add(LSTM(64, return_sequences=True, input_shape=(x_size, 1)))
model.add(Dropout(0.2))
model.add(BatchNormalization())
model.add(LSTM(64))
model.add(Dropout(0.2))
model.add(Dense(y_size))

# 컴파일 & 학습
model.compile(loss='mse', optimizer='adam')
early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

model.fit(
    x_train, y_train,
    validation_data=(x_test, y_test),
    epochs=20,
    batch_size=10,
    callbacks=[early_stop],
    verbose=1
)
model.save('TSLA2.model')
pred = model.predict(x_test)

# 역정규화 (원래 가격으로 복원)
y_test_inv = scaler.inverse_transform(y_test.reshape(-1,1))
pred_inv = scaler.inverse_transform(pred)

# 시각화
fig = plt.figure(figsize=(20, 10))
ax = fig.add_subplot(111)
ax.plot(y_test, label='True')
ax.plot(pred, label='Prediction')
ax.plot(y_test_inv, label='True inverse')
ax.plot(pred_inv, label='Pred inverse')
ax.legend()
plt.show()

