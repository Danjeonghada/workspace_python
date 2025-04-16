import numpy as np
import pickle
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import os

# 데이터 로드
data_dir = "naver_data"
x_train = np.load(os.path.join(data_dir, 'x_train.npy'))
y_train = np.load(os.path.join(data_dir, 'y_train.npy'))
x_test = np.load(os.path.join(data_dir, 'x_test.npy'))
y_test = np.load(os.path.join(data_dir, 'y_test.npy'))

with open(os.path.join(data_dir, 'tokenizer.pkl'), 'rb') as f:
    tokenizer = pickle.load(f)
with open(os.path.join(data_dir, 'meta_info.txt'), encoding='utf-8') as f:
    meta = {
        line.strip().split('=')[0]: line.strip().split('=')[1]
        for line in f if '=' in line
    }
    max_len = int(meta['max_len'])
    vocab_size = int(meta['vocab_size'])

# 모델 생성
print(f"max_len: {max_len}, vocab_size: {vocab_size}")
model = Sequential()
model.add(Embedding(input_dim=vocab_size, output_dim=100, input_length=max_len))
model.add(LSTM(128))
model.add(Dense(1, activation='sigmoid'))
model.compile(optimizer='rmsprop',
              loss='binary_crossentropy', metrics=['acc'])

# 콜백
es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=4)
mc = ModelCheckpoint('best_lstm_model.h5', monitor='val_acc',
                     mode='max', verbose=1, save_best_only=True)

# 학습 전 확인
print(f"x_train.shape: {x_train.shape}")
print(f"y_train.shape: {y_train.shape}")

# 학습
model.fit(x_train, y_train, epochs=15,
          batch_size=64, validation_split=0.2, callbacks=[es, mc])

# 테스트 평가
print("test_acc:", model.evaluate(x_test, y_test)[1])
