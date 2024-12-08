from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import json
import numpy as np
import tensorflow as tf
from sklearn.metrics.pairwise import cosine_similarity
import random
import math
from googletrans import Translator
from langdetect import detect



translator = Translator()
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
UPLOAD_FOLDER = 'static/uploads'
PRODUCTS_PER_PAGE = 12
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def Translate(word):
    try:
        return translator.translate(word, src="en", dest="ar").text
    except:
        return word




with open('static/extracted_product_features.json', 'r', encoding='utf-8') as f:
    features_data = json.load(f)

with open('static/formatted_products.json', 'r', encoding='utf-8') as f:
    formatted_products = json.load(f)

def contains_pattern(text, pattern):
    if not text or not pattern:
        return False
    
    i = 0  # index for pattern
    j = 0  # index for text
    
    while i < len(pattern) and j < len(text):
        if pattern[i] == text[j]:
            i += 1
        j += 1
    
    return i == len(pattern)

@app.route('/', methods=['GET'])
def index():
    page = request.args.get('page', 1, type=int)
    all_random_products = random.sample(formatted_products, len(formatted_products))
    
    total_products = len(all_random_products)
    total_pages = math.ceil(total_products / PRODUCTS_PER_PAGE)
    start_idx = (page - 1) * PRODUCTS_PER_PAGE
    end_idx = start_idx + PRODUCTS_PER_PAGE
    current_page_products = all_random_products[start_idx:end_idx]
    
    return render_template('index.html', 
                         similar_images=current_page_products,
                         page=page,
                         total_pages=total_pages)

@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)
    
    print(f"Received query: {query}")
    
    if query:
        try:
            detected_lang = detect(query)
            print(f"Detected language: {detected_lang}")
        except Exception as e:
            print(f"Language detection error: {e}")
            detected_lang = 'en'
            
        search_results = []
        
        if detected_lang in ['ar', 'fa']:
            print("Processing Arabic search...")
            for product in formatted_products:
                category_ar = product.get('category_ar', '')
                description_ar = product.get('description_ar', '')
                
                # Split query into words and check each word
                query_words = query.split()
                for word in query_words:
                    if (contains_pattern(category_ar, word) or 
                        contains_pattern(description_ar, word)):
                        search_results.append(product)
                        print(f"Found match for '{word}' in: {category_ar} or {description_ar}")
                        break
        else:
            print("Processing English search...")
            for product in formatted_products:
                if (query.lower() in product['category'].lower() or 
                    query.lower() in product.get('description', '').lower()):
                    search_results.append(product)
                    
        similar_images = search_results
        print(f"Total results found: {len(search_results)}")
    elif request.method == 'POST':
        # Image search code remains the same
        if 'image' not in request.files:
            return redirect(request.url)

        uploaded_image = request.files['image']

        if uploaded_image.filename != '':
            image_path = os.path.join(UPLOAD_FOLDER, uploaded_image.filename)
            uploaded_image.save(image_path)

            uploaded_image_features = extract_features(image_path)
            uploaded_image_features = uploaded_image_features / np.linalg.norm(uploaded_image_features)
            similar_images_ids = find_similar_images(uploaded_image_features)   
            session['search_result_ids'] = similar_images_ids
            similar_images = [
                product for product in formatted_products 
                if product['id'] in session['search_result_ids']
            ]
        else:
            return redirect(request.url)
    else:
        similar_images = formatted_products

    # If it's an AJAX request (from speech recognition)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'products': similar_images[:PRODUCTS_PER_PAGE]
        })

    total_products = len(similar_images)
    total_pages = math.ceil(total_products / PRODUCTS_PER_PAGE)
    start_idx = (page - 1) * PRODUCTS_PER_PAGE
    end_idx = start_idx + PRODUCTS_PER_PAGE
    
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