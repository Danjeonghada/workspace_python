import numpy as np

# 활성 함수
def step_function(sum):
    if sum > 0:
        return 1
    return 0

class Perceptron:
    def __init__(self, input_size):
        self.w = np.zeros(input_size + 1) # +1은 bias

    def predict(self, inputs):
        sum = np.dot(inputs, self.w[1:]) + self.w[0]
        return step_function(sum)

    def train(self, train_inputs, labels, lr=0.01, epochs=100):
        for _ in range(epochs):
            for inputs, label in zip(train_inputs, labels):
                prediction = self.predict(inputs)
                self.w[1:] += lr * (label - prediction) * inputs
                self.w[0]  += lr * (label - prediction)

# and 연산 데이터
train_data = np.array([[0, 0]
                      ,[0, 1]
                      ,[1, 0]
                      ,[1, 1]])
# labels = np.array([0, 0, 0, 1]) # and 정답
# labels = np.array([0, 1, 1, 1])   # or 정답
labels = np.array([0, 1, 1, 0])   # xor 정답
model = Perceptron(2)
model.train(train_data, labels, lr=0.1)
# 예측 결과
for i, v in zip(train_data, labels):
    pred = model.predict(i)
    print(f"입력:{i}, 예측:{pred}, 실제:{v}")
print(model)
print(model.w)
