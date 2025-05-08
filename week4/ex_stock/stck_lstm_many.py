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
scaler = MinMaxScaler(feature_range=(0, 1))
df['Close'] = scaler.fit_transform((df['Close'].values.reshape(-1, 1)))
joblib.dump(scaler, 'tsla3_scaler.pkl')  # 저장 (복원을 위해)

# 시계열 데이터 생성
def create_sequences(p_data, seq_length, size):
    result = []
    total_len = seq_length + size
    for i in range(len(p_data) - total_len + 1):
        x = p_data[i: i + seq_length]
        y = p_data[i + seq_length: i + total_len]
        result.append(np.concatenate([x, y]))
    return np.array(result)
x_size = 50
y_size = 5
dataset = create_sequences(df['Close'].values, x_size, y_size)
print(dataset.shape)

# 학습/테스트 분할
train_size = int(len(dataset) * 0.9)
train_data = dataset[:train_size]
test_data = dataset[train_size:]

x_train = train_data[:, :x_size] # 50개
y_train = train_data[:, x_size:] # 5개
x_test = test_data[:, :x_size]
y_test = test_data[:, x_size:]

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

# 학습
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
model.save('TSLA_5day.model')
pred = model.predict(x_test)

plt.figure(figsize=(20, 10))
for i in range(y_size):
    plt.subplot(y_size, 1, i +1)
    plt.plot(y_test[:, i], label='true')
    plt.plot(pred[:, i], label='pred')
    plt.title(f'day {i+1}')
    plt.legend()
plt.tight_layout()
plt.show()
