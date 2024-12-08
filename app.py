from flask import Flask, render_template, request, redirect, url_for, session
import os
import json
import numpy as np
import tensorflow as tf
from sklearn.metrics.pairwise import cosine_similarity
import random
import math

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for session

UPLOAD_FOLDER = 'static/uploads'
PRODUCTS_PER_PAGE = 12
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

with open('static/extracted_product_features.json', 'r') as f:
    features_data = json.load(f)

with open('static/formatted_products.json', 'r') as f:
    formatted_products = json.load(f)

@app.route('/', methods=['GET'])
def index():
    page = request.args.get('page', 1, type=int)
    # Get 12 random products to display
    all_random_products = random.sample(formatted_products, len(formatted_products))
    
    # Calculate pagination values
    total_products = len(all_random_products)
    total_pages = math.ceil(total_products / PRODUCTS_PER_PAGE)
    start_idx = (page - 1) * PRODUCTS_PER_PAGE
    end_idx = start_idx + PRODUCTS_PER_PAGE
    
    # Get products for current page
    current_page_products = all_random_products[start_idx:end_idx]
    
    return render_template('index.html', 
                         similar_images=current_page_products,
                         page=page,
                         total_pages=total_pages)

@app.route('/search', methods=['GET', 'POST'])
def search():
    page = request.args.get('page', 1, type=int)
    
    if request.method == 'POST':
        if 'image' not in request.files:
            return redirect(request.url)

        uploaded_image = request.files['image']

        if uploaded_image.filename != '':
            image_path = os.path.join(UPLOAD_FOLDER, uploaded_image.filename)
            uploaded_image.save(image_path)

            uploaded_image_features = extract_features(image_path)
            uploaded_image_features = uploaded_image_features / np.linalg.norm(uploaded_image_features)
            similar_images_ids = find_similar_images(uploaded_image_features)
            
            # Store just the IDs in session
            session['search_result_ids'] = similar_images_ids
        else:
            return redirect(request.url)
    
    # Get products based on stored IDs or show all products
    if 'search_result_ids' in session:
        similar_images = [
            product for product in formatted_products 
            if product['id'] in session['search_result_ids']
        ]
    else:
        similar_images = formatted_products

    # Calculate pagination values
    total_products = len(similar_images)
    total_pages = math.ceil(total_products / PRODUCTS_PER_PAGE)
    start_idx = (page - 1) * PRODUCTS_PER_PAGE
    end_idx = start_idx + PRODUCTS_PER_PAGE
    
    # Get products for current page
    current_page_products = similar_images[start_idx:end_idx]

    return render_template('index.html', 
                         similar_images=current_page_products,
                         page=page,
                         total_pages=total_pages)

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
    similar_images = []

    for image_data in features_data:
        image_features = np.array(image_data['features'])
        image_features = image_features / np.linalg.norm(image_features)
        similarity_score = cosine_similarity([uploaded_features], [image_features])[0][0]
        if similarity_score > 0.30:
            similar_images.append((image_data['id'], similarity_score))

    similar_images.sort(key=lambda x: x[1], reverse=True)
    return [img_id for img_id, _ in similar_images]

if __name__ == "__main__":
    app.run(debug=True)