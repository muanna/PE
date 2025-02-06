
"""import cv2
import numpy as np
import os
from flask import Flask, request, send_file

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def frequency_separation(image_path):
  """  """Apply frequency separation to smooth the skin while keeping details."""   """
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
  """  """Enhance details while keeping a natural look."""         """
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
"""



"""
import cv2
import numpy as np
import os
from flask import Flask, request, send_file

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def enhance_image(image_path):
  """  """Apply lightweight skin enhancement, spot reduction, and sharpening with realistic effects.""""""""
    image = cv2.imread(image_path)
    if image is None:
        return None
    
    # Convert to LAB color space for better skin tone handling
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Adaptive contrast enhancement using CLAHE (milder contrast boost)
    clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))  # Reduced clipLimit for mild enhancement
    l = clahe.apply(l)
    enhanced_lab = cv2.merge([l, a, b])
    enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
    
    # Use edge-preserving filter for skin smoothing (adjusted for subtlety)
    smooth = cv2.edgePreservingFilter(enhanced, flags=1, sigma_s=20, sigma_r=0.2)  # Subtle smoothing

    # Apply gentle sharpening without overdoing it
    gaussian = cv2.GaussianBlur(smooth, (0, 5), 1.5)  # Reduced Gaussian blur for milder effect
    high_pass = cv2.subtract(smooth, gaussian)
    sharpened = cv2.addWeighted(smooth, 0.5, high_pass, 0.3, 0)  # Blend sharpen effect softly

    # Save processed image
    processed_path = os.path.join(PROCESSED_FOLDER, "enhanced.jpg")
    cv2.imwrite(processed_path, sharpened)
    return processed_path

@app.route('/auto_fix', methods=['POST'])
def auto_fix():
    if 'image' not in request.files:
        return {"error": "No image uploaded"}, 400

    file = request.files['image']
    
    # Validate file format
    if not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        return {"error": "Unsupported file format. Use PNG, JPG, or JPEG."}, 400

    filename = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filename)

    # Process image with lightweight enhancement
    enhanced_image = enhance_image(filename)
    if enhanced_image is None:
        return {"error": "Invalid image file"}, 400

    return send_file(enhanced_image, mimetype='image/jpeg')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
"""



"""

import cv2
import numpy as np
import os
from flask import Flask, request, send_file

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def frequency_separation(image):
"""    """Smooth skin while preserving fine details."""   """
    h, w, _ = image.shape
    blur_ksize = (max(51, (w // 20) | 1), max(51, (h // 20) | 1))  # Ensure odd numbers
    sigma = max(10, min(50, w//50))

    image_float = image.astype(np.float32) / 255.0
    low_freq = cv2.GaussianBlur(image_float, blur_ksize, sigma)
    high_freq = image_float - low_freq

    blended = low_freq + high_freq * 0.3  # Reduced from 0.6 to 0.3
    blended = np.clip(blended * 255, 0, 255).astype(np.uint8)
    
    return blended

def apply_makeup(image):
"""    """Enhance eyes, lips, and overall makeup appearance."""    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Darken eyebrows using edge detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 20, 100)  # Reduced thresholds from (50, 150) to (20, 100)
    edges = cv2.dilate(edges, None, iterations=1)
    image[edges > 100] = [50, 50, 50]  # Darker strokes

    # Enhance lips (boost red tones)
    lower_lip = np.array([0, 50, 50])
    upper_lip = np.array([10, 255, 255])
    mask = cv2.inRange(hsv, lower_lip, upper_lip)

    red_tint = np.full_like(image, (0, 0, 150), dtype=np.uint8)
    red_lips = cv2.addWeighted(image, 1.2, red_tint, 0.5, 0)  # Reduced from 1.5 to 1.2
    image[mask > 0] = red_lips[mask > 0]

    # Apply slight eye shadow effect
    eye_shadow_mask = cv2.inRange(hsv, np.array([100, 50, 50]), np.array([140, 255, 255]))
    purple_tint = np.full_like(image, (100, 50, 150), dtype=np.uint8)
    eye_shadow = cv2.addWeighted(image, 1.1, purple_tint, 0.7, 0)  # Reduced from 1.3 to 1.1
    image[eye_shadow_mask > 0] = eye_shadow[eye_shadow_mask > 0]

    return image

def adjust_lighting(image):
"""    """Improve brightness and contrast."""   """
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))  # Reduced from 3.0 to 1.5
    l = clahe.apply(l)
    
    enhanced_lab = cv2.merge([l, a, b])
    return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

def facial_contour(image):
 """   """Apply subtle contouring effects."""   """
    blurred = cv2.GaussianBlur(image, (0, 0), 5)
    high_pass = cv2.subtract(image, blurred)
    return cv2.addWeighted(image, 1.1, high_pass, 0.1, 0)  # Reduced from 1.2, 0.3 to 1.1, 0.1

@app.route('/auto_fix', methods=['POST'])
def smooth_and_sharpen_api():
    if 'image' not in request.files:
        return {"error": "No image uploaded"}, 400

    file = request.files['image']
    
    if not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        return {"error": "Unsupported file format. Use PNG, JPG, or JPEG."}, 400

    filename = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filename)

    image = cv2.imread(filename)
    if image is None:
        return {"error": "Invalid image file"}, 400

    # Apply all enhancements step by step
    image = frequency_separation(image)  # Skin smoothing
    image = apply_makeup(image)  # Simulated makeup
    image = adjust_lighting(image)  # Lighting & contrast
    image = facial_contour(image)  # Contouring effect

    processed_path = os.path.join(PROCESSED_FOLDER, "enhanced.jpg")
    cv2.imwrite(processed_path, image)

    return send_file(processed_path, mimetype='image/jpeg')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
"""





import cv2
import numpy as np
import os
from flask import Flask, request, send_file

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
VIBRANT_FOLDER = "vibrant"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(VIBRANT_FOLDER, exist_ok=True)

def frequency_separation(image_path):
    """Apply frequency separation to smooth the image while retaining details."""
    image = cv2.imread(image_path)
    if image is None:
        return None

    image_float = image.astype(np.float32) / 255.0
    low_freq = cv2.GaussianBlur(image_float, (11, 41), 10)
    high_freq = image_float - low_freq
    blended = low_freq + high_freq * 0.5
    blended = np.clip(blended * 255, 0, 255).astype(np.uint8)

    smoothed_path = os.path.join(PROCESSED_FOLDER, "smoothed.jpg")
    cv2.imwrite(smoothed_path, blended)
    return smoothed_path

def unsharp_mask(image_path):
    """Apply unsharp masking to enhance edges and details."""
    image = cv2.imread(image_path)
    if image is None:
        return None

    blurred = cv2.GaussianBlur(image, (0, 0), 2)
    sharpened = cv2.addWeighted(image, 1.7, blurred, -0.7, 0)

    sharpened_path = os.path.join(PROCESSED_FOLDER, "sharpened.jpg")
    cv2.imwrite(sharpened_path, sharpened)
    return sharpened_path

def enhance_colors(image_path):
    """Enhance colors with a subtle boost to vibrancy and warmth."""
    image = cv2.imread(image_path)
    if image is None:
        return None
    
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    a = cv2.addWeighted(a, 1.05, a, 0, 3)  # Slight red boost
    b = cv2.addWeighted(b, 1.05, b, 0, 3)  # Slight blue boost
    
    enhanced_lab = cv2.merge([l, a, b])
    enhanced_image = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
    
    vibrant_path = os.path.join(VIBRANT_FOLDER, "vibrant.jpg")
    cv2.imwrite(vibrant_path, enhanced_image)
    return vibrant_path

@app.route('/auto_fix', methods=['POST'])
def smooth_and_sharpen_api():
    if 'image' not in request.files:
        return {"error": "No image uploaded"}, 400

    file = request.files['image']
    if not file.filename.lower().endswith((".png", ".jpg", ".jpeg" ,".webp")):
        return {"error": "Unsupported file format. Use PNG, JPG, or JPEG."}, 400

    filename = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filename)

    smoothed_image = frequency_separation(filename)
    if smoothed_image is None:
        return {"error": "Invalid image file"}, 400

    sharpened_image = unsharp_mask(smoothed_image)
    if sharpened_image is None:
        return {"error": "Error sharpening image"}, 500

    vibrant_image = enhance_colors(sharpened_image)
    if vibrant_image is None:
        return {"error": "Error enhancing colors"}, 500

    return send_file(vibrant_image, mimetype='image/jpeg')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
