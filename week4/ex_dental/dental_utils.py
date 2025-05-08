import numpy as np
from keras.applications import vgg16
from keras.preprocessing.image import load_img, img_to_array
import matplotlib.pyplot as plt
import os
# pip install split-folders
import splitfolders

def preprocess_image(img_path):
    image = load_img(img_path, target_size=(224, 224))
    img_array = img_to_array(image).reshape(1, 224, 224, 3)
    return image, img_array

def display_predict(image, prediction, labels):
    idx = np.argmax(prediction)
    plt.imshow(image)
    plt.title(f'{labels[idx]}-{prediction[0][idx]*100:.2f}%')
    plt.axis('off')
    plt.show()

def imgnet_predict(p_model, p_file):
    image, test_array = preprocess_image(p_file)
    plt.imshow(image)
    plt.show()
    test = vgg16.preprocess_input(test_array)
    pred = p_model.predict(test)
    label = vgg16.decode_predictions(pred)
    pred_cls = label[0][0]
    print(pred_cls[1], pred_cls[2] * 100)
if __name__ == '__main__':
    # model = vgg16.VGG16()
    # model.summary()
    # path = '../../dataset/imageNet/'
    # f_list = os.listdir(path)
    # for f in f_list:
    #     imgnet_predict(model, path + f)
    before_dir = '../../dataset/whale'
    after_dir = '../../dataset/whale_split'
    train_ratio = 0.8
    val_ratio = 0.0
    test_ratio = 0.2
    splitfolders.ratio(input=before_dir
            ,output=after_dir ,seed=1
            ,ratio=(train_ratio, val_ratio, test_ratio))