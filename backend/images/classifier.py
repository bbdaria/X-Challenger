from typing import Any
from .static_analyzer import StaticImageAnalyzer
import torch
from torchvision import transforms
from PIL import Image
import numpy as np
import os
import sys

# Add TrueFake detector to sys.path for import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../TrueFake-IJCNN25/detector')))
from networks import ImageClassifier as TrueFakeImageClassifier

class MinimalSettings:
    def __init__(self):
        self.arch = 'nodown'
        self.freeze = False
        self.prototype = True
        self.num_centers = 1

class ImageClassifier:
    def __init__(self, model_path: str = None):
        # Path to the best.pt model
        MODEL_PATH = model_path or os.path.abspath(os.path.join(os.path.dirname(__file__), 'best.pt'))
        self.static_analyzer = StaticImageAnalyzer()
        # Create settings object as expected by the model
        settings = MinimalSettings()
        self.model = TrueFakeImageClassifier(settings)
        self.model.eval()
        # Load weights
        state_dict = torch.load(MODEL_PATH, map_location=torch.device('cpu'))
        self.model.load_state_dict(state_dict)
        # Preprocessing pipeline (match what TrueFake expects)
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def classify_image(self, image_path):
        """
        Classify a single image as REAL or AI-generated (FAKE).
        Args:
            image_path (str): Path to the image file.
        Returns:
            dict: static analysis, prediction, score
        """
        # Step 1: Static analysis
        static_results = self.static_analyzer.analyze(image_path)
        print("Static analysis results:", static_results)

        # Load and preprocess the image
        img = Image.open(image_path).convert('RGB')
        img_tensor = self.transform(img).unsqueeze(0)  # Add batch dimension

        # Predict
        with torch.no_grad():
            logit = self.model(img_tensor)
            print(f"Raw model output tensor: {logit}")
            logit_value = float(logit.item())
            prob_fake = float(torch.sigmoid(logit).item())
            label = 'FAKE' if logit_value > 0 else 'REAL'
        print(f"Prediction: {label} (logit: {logit_value:.4f}, prob_fake: {prob_fake:.4f})")
        return {
            "static_analysis": static_results,
            "prediction": label,
            "logit": logit_value,
            "prob_fake": prob_fake
        }

