from keras.models import load_model
from keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np

test_dir = '../../dataset/dental_image/test/'
model = load_model('dental100.h5')

test_datagen = ImageDataGenerator()
test_generator = test_datagen.flow_from_directory(
    test_dir, target_size=(224, 224), batch_size=32
   ,class_mode='categorical', shuffle=False
)
pred = model.predict(test_generator)
y_pred = np.argmax(pred, axis=1)
y_true = test_generator.classes
class_labels = list(test_generator.class_indices.keys())
print("분류 평가 결과\n")
print("혼동 행렬 confusion_matrix")
print(confusion_matrix(y_true, y_pred))