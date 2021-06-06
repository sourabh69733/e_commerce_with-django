import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from tensorflow import keras
import tensorflow as tf
import numpy as np


model_path = "core/mnist_ml_pred/cassava_model"

def preprocess_img(img_path):
    img = keras.preprocessing.image.load_img(img_path)
    img = keras.preprocessing.image.img_to_array(
        img
    )
    img = img/255.0
    img = tf.image.resize(img, [224, 224])
    return img


img_path = "media_root/documents/train-cbb-1.jpg"
img = preprocess_img(img_path)

loaded_model = tf.keras.models.load_model(model_path)

print(loaded_model)
