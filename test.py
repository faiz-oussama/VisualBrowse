from langdetect import detect, detect_langs
import json
from googletrans import Translator
import time

translator = Translator()

# Detect a single language
text = "هاتف"
language = detect(text)
print(f"Detected language: {language}")

# Load the original products
file_path = 'static/formatted_products.json'
with open(file_path, 'r', encoding='utf-8') as f:
    products = json.load(f)

def translate_to_arabic(text):
    try:
        if not text:
            return ""
        # Add delay to avoid rate limiting
        time.sleep(1)
        return translator.translate(text, src='en', dest='ar').text
    except Exception as e:
        print(f"Translation error for text '{text}': {e}")
        return text

print(f"Starting translation of {len(products)} products...")

# Translate each product
for i, product in enumerate(products):
    print(f"Translating product {i+1}/{len(products)}")
    
    # Translate category
    if 'category' in product:
        product['category_ar'] = translate_to_arabic(product['category'])
        print(f"Category: {product['category']} -> {product['category_ar']}")
    
    # Translate description
    if 'description' in product:
        product['description_ar'] = translate_to_arabic(product['description'])
        print(f"Description translated")

# Save back to the same file
with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

print("Translation completed! File updated with Arabic translations")