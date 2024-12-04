from flask import Flask, render_template, request, redirect, url_for
import os
from script import find_similar_images  # Import the function from script.py

app = Flask(__name__)

# Ensure the uploads folder exists
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    similar_images = []

    if request.method == 'POST':
        # Check if the 'image' field exists in the form
        if 'image' not in request.files:
            return redirect(request.url)

        uploaded_image = request.files['image']

        if uploaded_image.filename != '':
            # Save the uploaded image
            image_path = os.path.join(UPLOAD_FOLDER, uploaded_image.filename)
            uploaded_image.save(image_path)

            # Get similar images based on the uploaded image
            similar_images = find_similar_images(image_path)

    return render_template('index.html', similar_images=similar_images)

if __name__ == "__main__":
    app.run(debug=True)
