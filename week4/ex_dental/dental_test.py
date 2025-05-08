from keras.models import load_model
from dental_utils import preprocess_image, display_predict

model = load_model('dental100.h5')

labels = ['cured', 'decayed', 'healthy']

ima_path = '../../dataset/dental_image/test/healthy/1.jpg'

image, input_array = preprocess_image(ima_path)
pred = model.predict(input_array)
display_predict(image, pred, labels)