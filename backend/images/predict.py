import sys
import numpy as np
import tensorflow as tf
import cv2

MODEL_PATH = 'model/ai_imageclassifier.h5'

# Load the model once at module level for efficiency
model = tf.keras.models.load_model(MODEL_PATH)

def classify_image(image_path):
    """
    Classify a single image as REAL or AI-generated (FAKE).
    Args:
        image_path (str): Path to the image file.
    Returns:
        str: 'REAL' or 'AI'
    """
    # Load and preprocess the image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not load image at {image_path}")
        return None
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = tf.image.resize(img, (32, 32)).numpy()
    img_norm = img_resized / 255.0
    img_input = np.expand_dims(img_norm, axis=0)

    # Predict
    y_pred = model.predict(img_input)
    label = 'REAL' if y_pred > 0.5 else 'AI'
    print(f"Prediction: {label} (score: {float(y_pred):.4f})")
    return label
