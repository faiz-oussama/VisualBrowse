from serpapi import GoogleSearch
import json

categories = [
    "Laptops", "Smartphones", "Tablets", "Smartwatches", "Headphones", "Cameras",
    "Coffee makers", "Blenders", "Vacuum cleaners", "Microwave ovens", "Refrigerators", "Cookware sets",
    "Men's shirts", "Women's dresses", "Shoes", "Watches", "Handbags", "Sunglasses",
    "Vitamins", "Fitness trackers", "Electric toothbrushes", "Hair dryers", "Skin care products", "Massage chairs",
    "Board games", "Action figures", "Building blocks", "Educational toys", "Remote control cars", "Puzzles",
    "Bicycles", "Camping gear", "Hiking boots", "Yoga mats", "Fitness equipment", "Sports apparel",
    "Car accessories", "Tires", "Car batteries", "GPS devices", "Car seats", "Dash cams",
    "Fiction novels", "Non-fiction books", "Children's books", "Textbooks", "Cookbooks", "Self-help books",
    "Makeup", "Skincare", "Haircare", "Fragrances", "Nail care", "Beauty tools",
    "Printers", "Office chairs", "Desk organizers", "Stationery", "Projectors", "Whiteboards" 
]

all_products = []

for category in categories:
    params = {
        "engine": "google_shopping",
        "q": category,
        "api_key": "dd636bf5d7a2b3d16d42847f5d84cd7e3711d2bb471e346d8979f507c48b97cd"
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    for product in results.get("shopping_results", []):
        product_data = {
            "id": product.get("product_id"),
            "title": product.get("title"),
            "description": product.get("title"),
            "price": product.get("price"),
            "discountPercentage": None,
            "rating": product.get("rating"),
            "stock": None,
            "brand": product.get("source"),
            "category": category,
            "thumbnail": product.get("thumbnail"),
            "images": [product.get("thumbnail")]
        }
        all_products.append(product_data)

with open('formatted_products.json', 'w') as file:
    json.dump(all_products, file, indent=4)