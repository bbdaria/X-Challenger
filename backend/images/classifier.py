from typing import Any
import tensorflow as tf
from .static_analyzer import StaticImageAnalyzer
import cv2
import numpy as np

class ImageClassifier:
    def __init__(self, model_path: str = None):
        MODEL_PATH = 'ai_imageclassifier.h5'
        # Load model without compiling to avoid reduction='auto' error
        self.model = tf.keras.models.load_model(MODEL_PATH, compile=False)
        # Compile with a valid loss function
        self.model.compile(
            loss=tf.keras.losses.BinaryCrossentropy(reduction='sum_over_batch_size'),
            optimizer='adam'
        )
        self.static_analyzer = StaticImageAnalyzer()

    def classify_image(self, image_path):
        """
        Classify a single image as REAL or AI-generated (FAKE).
        Args:
            image_path (str): Path to the image file.
        Returns:
            str: 'REAL' or 'AI'
        """
        # Step 1: Static analysis
        static_results = self.static_analyzer.analyze(image_path)
        print("Static analysis results:", static_results)

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
        y_pred = self.model.predict(img_input)
        label = 'REAL' if y_pred > 0.5 else 'AI'
        print(f"Prediction: {label} (score: {float(y_pred):.4f})")
        return {
            "static_analysis": static_results,
            "prediction": label,
            "score": float(y_pred)
        }

