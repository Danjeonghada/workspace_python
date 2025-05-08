import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout, BatchNormalization
from keras.callbacks import EarlyStopping

# 데이터 로드
df = pd.read_excel('TSLA_20190101_20250331.xlsx')
print(df.head())

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
model.save('TSLA.model')
pred = model.predict(x_test)

# 시각화
fig = plt.figure(figsize=(20, 10))
ax = fig.add_subplot(111)
ax.plot(y_test, label='True')
ax.plot(pred, label='Prediction')
ax.legend()
plt.show()

