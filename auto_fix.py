import cv2
import numpy as np
import os
from flask import Flask, request, send_file

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def frequency_separation(image_path):
    """Apply frequency separation to smooth the skin while keeping details."""
    image = cv2.imread(image_path)
    if image is None:
        return None

    h, w, _ = image.shape
    blur_ksize = (max(51, (w // 20) | 1), max(51, (h // 20) | 1))  # Force odd numbers
  # Dynamically adjust kernel size
    sigma = max(10, min(50, w//50))  # Adjust sigma dynamically

    # Convert to float for better blending
    image_float = image.astype(np.float32) / 255.0

    # Low frequency (smoothed skin)
    low_freq = cv2.GaussianBlur(image_float, blur_ksize, sigma)

    # High frequency (texture details)
    high_freq = image_float - low_freq

    # Blend back, slightly increasing texture contribution
    blended = low_freq + high_freq * 0.6  # Increased from 0.5 to 0.6
    blended = np.clip(blended * 255, 0, 255).astype(np.uint8)

    smoothed_path = os.path.join(PROCESSED_FOLDER, "smoothed.jpg")
    cv2.imwrite(smoothed_path, blended)
    return smoothed_path

def unsharp_mask(image_path):
    """Enhance details while keeping a natural look."""
    image = cv2.imread(image_path)
    if image is None:
        return None

    h, w, _ = image.shape
    blur_radius = max(1, min(2, w//500))  # Adapt sharpening to image size

    # Slightly sharpen the image while keeping it natural
    blurred = cv2.GaussianBlur(image, (0, 0), blur_radius)
    sharpened = cv2.addWeighted(image, 1.8, blurred, -0.8, 0)  # Adjusted weights

    sharpened_path = os.path.join(PROCESSED_FOLDER, "sharpened.jpg")
    cv2.imwrite(sharpened_path, sharpened)
    return sharpened_path

@app.route('/auto_fix', methods=['POST'])
def smooth_and_sharpen_api():
    if 'image' not in request.files:
        return {"error": "No image uploaded"}, 400

    file = request.files['image']
    
    # Validate file format
    if not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        return {"error": "Unsupported file format. Use PNG, JPG, or JPEG."}, 400

    filename = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filename)

    # Step 1: Smooth skin while keeping texture
    smoothed_image = frequency_separation(filename)
    if smoothed_image is None:
        return {"error": "Invalid image file"}, 400

    # Step 2: Sharpen carefully
    sharpened_image = unsharp_mask(smoothed_image)
    return send_file(sharpened_image, mimetype='image/jpeg')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
