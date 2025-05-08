import os
import sys
import argparse
from pathlib import Path
from typing import Any, Dict
import logging

import torch
from PIL import Image
from torchvision import transforms

# Static analyzer for metadata/watermarks
from .static_analyzer import StaticImageAnalyzer
from .networks import ImageClassifier as TrueFakeImageClassifier

logger = logging.getLogger("uvicorn.error")

class MinimalSettings:
    """
    Settings stub matching TrueFake's expected args for networks.ImageClassifier.
    Use the same IDs as in training (e.g., 'sd2:pre&...').
    """
    def __init__(self):
        # Name is unused for inference
        self.name = 'inference'
        # Not training, so flags can be default
        self.arch = 'nodown'  # use 'nodown' to enable prototype branch (E2P)
        self.freeze = False
        self.prototype = True  # enable prototype ScoresLayer
        self.num_centers = 1
        # data_keys not used here
        self.data_keys = ''
        self.device = 'cpu'

class Wrapper:
    """
    Combines static analysis with the learned TrueFake classifier.
    """
    def __init__(self, ckpt_path: str = None):
        # Determine checkpoint location
        default_ckpt = Path(__file__).resolve().parent / 'best.pt'
        self.ckpt = Path(ckpt_path) if ckpt_path else default_ckpt

        # Initialize static analyzer
        self.static_analyzer = StaticImageAnalyzer()

        # Build the classifier using stub settings
        settings = MinimalSettings()
        self.classifier = TrueFakeImageClassifier(settings)
        # Load pretrained weights
        logger.info(f"Loading model weights from {self.ckpt}")
        state = torch.load(self.ckpt, map_location='cpu')
        self.classifier.load_state_dict(state)
        self.classifier.eval()
        logger.info("Model loaded and set to eval mode.")

        # Preprocessing pipeline matching training setup
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
        ])

    def classify_image(self, image_path: str) -> Dict[str, Any]:
        logger.info(f"Classifying image: {image_path}")
        # 1) Static analysis
        static_out = self.static_analyzer.analyze(image_path)
        logger.info(f"Static analysis results: {static_out}")
        for res in static_out:
            if (res.get('analyzer') == 'analyze_metadata' and res.get('ai_related')) or \
               (res.get('analyzer') == 'detect_watermark' and res.get('found')):
                logger.info(f"Static analysis detected fake: {res}")
                return {
                    'result': 'fake',
                    'model': res.get('details', 'unknown'),
                    'prob_fake': 1.0
                }

        # 2) CNN inference
        try:
            img = Image.open(image_path).convert('RGB')
            tensor = self.transform(img).unsqueeze(0)
            with torch.no_grad():
                out = self.classifier(tensor)
                prob_fake = float(torch.sigmoid(out * 5).item())
                result = 'fake' if prob_fake > 0.5 else 'real'
            logger.info(f"CNN prediction: result={result}, prob_fake={prob_fake}")
        except Exception as e:
            logger.error(f"Error during CNN inference: {e}")
            return {'result': 'error', 'error': str(e)}

        if result == 'fake':
            return {
                'result': 'fake',
                'model': 'A diffusion model',
                'prob_fake': prob_fake
            }
        else:
            return {
                'result': 'real',
                'prob_fake': prob_fake
            }