import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Flatten, Dense, Dropout
from keras.preprocessing.image import ImageDataGenerator
from keras.applications import VGG16

# train_dir = '../../dataset/dental_image/train'
# test_dir = '../../dataset/dental_image/test'
train_dir = '../../dataset/whale_split/train'
test_dir = '../../dataset/whale_split/test'


train_datagen = ImageDataGenerator(
    rotation_range=180, width_shift_range=0.2, height_shift_range=0.2
   ,horizontal_flip=True, vertical_flip=True, brightness_range=[0.5, 1.5]
)
test_datagen = ImageDataGenerator()
train_generator = train_datagen.flow_from_directory(
    train_dir, target_size=(224, 224)
   ,batch_size=32, class_mode='categorical'
)
test_generator = test_datagen.flow_from_directory(
    test_dir, target_size=(224, 224)
   ,batch_size=32, class_mode='categorical'
)
class_num = len(train_generator.class_indices)
print('labels:', train_generator.class_indices)
# pre-training 모델 (학습 되어 있는 모델 가져 오기)
base_model = VGG16(weights='imagenet', include_top=False
                  ,input_shape=(224, 224, 3))
# 학습 되어진 레이어는 학습이 안되게 고정
for layer in base_model.layers:
    layer.trainable = False
# fine-tuning (사전 학습되어 있는 모델을 새로운 작업에 맞게 조정)
model = Sequential([
    base_model, Flatten(), Dense(1024, activation='relu')
   ,Dropout(0.5), Dense(class_num, activation='softmax')
])
model.summary()
model.compile(loss='categorical_crossentropy', optimizer='adam'
             ,metrics=['acc'])
history = model.fit(train_generator,
                    steps_per_epoch=len(train_generator),
                    epochs=20,
                    validation_data=test_generator,
                    validation_steps=len(test_generator))
model.save('whale.h5')
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(history.history['acc'], label='train acc')
plt.plot(history.history['val_acc'], label='val acc')
plt.xlabel('epoch')
plt.ylabel('acc')
plt.legend()
plt.tight_layout()
plt.show()