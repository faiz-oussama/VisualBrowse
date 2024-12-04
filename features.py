import json
import requests
import tensorflow as tf
import numpy as np
from io import BytesIO
from PIL import Image

with open('formatted_products.json', 'r') as f:
    products = json.load(f)

model = tf.keras.applications.VGG16(weights='imagenet', include_top=False)

def process_image_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            img = img.resize((224, 224))
            img_array = tf.keras.preprocessing.image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = tf.keras.applications.vgg16.preprocess_input(img_array)
            features = model.predict(img_array)
            return features.flatten()
        else:
            print(f"Failed to fetch image from {url}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error processing image from {url}: {e}")
        return None

product_features = []

for product in products:
    image_url = product.get('thumbnail')
    product_id = product.get('id')
    features = process_image_from_url(image_url)
    if features is not None:
        product_features.append({
            'id': product_id,
            'features': features.tolist()
        })

with open('extracted_product_features.json', 'w') as f:
    json.dump(product_features, f, indent=4)