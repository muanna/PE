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
    """Apply frequency separation to smooth the image while retaining details."""
    image = cv2.imread(image_path)
    if image is None:
        return None

    # Convert to float for processing
    image_float = image.astype(np.float32) / 255.0

    # Lower Gaussian blur for better detail retention
    low_freq = cv2.GaussianBlur(image_float, (49, 31), 60)

    # Extract high-frequency details
    high_freq = image_float - low_freq

    # Blend back while smoothing, increasing high-frequency contribution
    blended = low_freq + high_freq * 0.5  # Increased from 0.2 to 0.5
    blended = np.clip(blended * 255, 0, 255).astype(np.uint8)

    smoothed_path = os.path.join(PROCESSED_FOLDER, "smoothed.jpg")
    cv2.imwrite(smoothed_path, blended)
    return smoothed_path

def unsharp_mask(image_path):
    """Apply unsharp masking to enhance edges and details."""
    image = cv2.imread(image_path)
    if image is None:
        return None

    # Reduce Gaussian blur effect to avoid over-softening
    blurred = cv2.GaussianBlur(image, (0, 0), 2)  # Lower blur

    # Fine-tuned unsharp mask formula (reduce blurriness)
    sharpened = cv2.addWeighted(image, 1.7, blurred, -0.7, 0)  # Adjusted weights

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

    # Step 1: Smooth while keeping texture
    smoothed_image = frequency_separation(filename)
    if smoothed_image is None:
        return {"error": "Invalid image file"}, 400

    # Step 2: Sharpen carefully
    sharpened_image = unsharp_mask(smoothed_image)
    return send_file(sharpened_image, mimetype='image/jpeg')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
