from flask import Flask, render_template, request, redirect, url_for
import os
import json
import numpy as np
import tensorflow as tf
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

with open('static/extracted_product_features.json', 'r') as f:
    features_data = json.load(f)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    similar_images = []

    if 'image' not in request.files:
        return redirect(request.url)

    uploaded_image = request.files['image']

    if uploaded_image.filename != '':
        image_path = os.path.join(UPLOAD_FOLDER, uploaded_image.filename)
        uploaded_image.save(image_path)

        uploaded_image_features = extract_features(image_path)

        uploaded_image_features = uploaded_image_features / np.linalg.norm(uploaded_image_features)

        similar_images_ids = find_similar_images(uploaded_image_features)

        with open('static/formatted_products.json', 'r') as f:
            formatted_products = json.load(f)

        similar_images = [
            product for product in formatted_products 
            if product['id'] in similar_images_ids
        ]

    return render_template('index.html', similar_images=similar_images)

def extract_features(image_path):
    img = tf.keras.preprocessing.image.load_img(image_path, target_size=(224, 224))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = tf.keras.applications.vgg16.preprocess_input(img_array)
    model = tf.keras.applications.VGG16(weights='imagenet', include_top=False)
    features = model.predict(img_array)
    features = features.flatten()
    return features

def find_similar_images(uploaded_features):
    similar_image_ids = []

    for image_data in features_data:
        image_features = np.array(image_data['features'])
        
        image_features = image_features / np.linalg.norm(image_features)
        
        similarity_score = cosine_similarity([uploaded_features], [image_features])[0][0]
        print(similarity_score)
        if similarity_score > 0.32:
            similar_image_ids.append(image_data['id'])

    return similar_image_ids

if __name__ == "__main__":
    app.run(debug=True)