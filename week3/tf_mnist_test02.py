from keras.models import load_model
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

model = load_model("mnist01")
# 이미지 로드
image = Image.open("nine.png")
# 이미지 크기 변환
image = image.resize((28, 28)).convert("L") # 28 x 28 흑백으로
image = 255 - np.array(image)
plt.imshow(image, cmap='Greys')
plt.show()
# 데이터 전처리
image_arr = np.array(image)
image_arr_re = image_arr.reshape(1, 784).astype('float32')/255.0
pred = model.predict(image_arr_re)
print(np.argmax(pred))