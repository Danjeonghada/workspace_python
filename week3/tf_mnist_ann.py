import matplotlib.pyplot as plt
from keras.datasets import mnist
from keras.utils import to_categorical
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense

(x_train, y_train), (x_test, y_test) = mnist.load_data()
print(f"학습 데이터:{x_train.shape}")
print(f"테스트 데이터:{x_test.shape}")
plt.imshow(x_train[0], cmap="Greys")
plt.show()
# 데이터 준비 2B x 2B = 784로
x_train_reshape = x_train.reshape(x_train.shape[0], 784).astype("float32")/255
x_test_reshape = x_test.reshape(x_test.shape[0], 784).astype("float32")/255
y_train_cate = to_categorical(y_train, 10)  # one hot encoding
y_test_cate = to_categorical(y_test, 10)
# 모델 구조 정의
model = Sequential()
model.add(Dense(512, input_dim=784, activation='relu'))
model.add(Dense(10, activation='softmax'))  # 10개의 output을 확률 값으로
model.summary()
# 최적화 방법 정의
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['acc'])
history = model.fit(x_train_reshape, y_train_cate
                   ,epochs=30, batch_size=100,validation_data=(x_test_reshape, y_test_cate))

print(f"학습 acc: {model.evaluate(x_train_reshape, y_train_cate)}")
print(f"테스트 acc: {model.evaluate(x_test_reshape, y_test_cate)}")
model.save("mnist01")
v_loss = history.history['val_loss']
loss = history.history['loss']
import numpy as np
cnt = np.arange(len(v_loss))
plt.plot(cnt, v_loss, c='red', label='test')
plt.plot(cnt, loss, c='blue', label='train')
plt.xlabel('epoch')
plt.ylabel('loss')
plt.show()
