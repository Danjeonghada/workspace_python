from keras.models import load_model
from keras.datasets import mnist
import numpy as np
import matplotlib.pyplot as plt

(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_test_sample = x_test[0].reshape(1, 784).astype("float32")/255
model = load_model("mnist01")
model.summary()
plt.imshow(x_test[0], cmap='Greys')
pred = model.predict(x_test_sample)
pred_cls = np.argmax(pred, axis=1)
print(pred_cls)
plt.show()