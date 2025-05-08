from typing import Callable, Dict, List
from PIL import Image
import os

class StaticImageAnalyzer:
    def __init__(self):
        self.analyzers: List[Callable[[str], Dict]] = []
        self.register_analyzer(self.detect_watermark)
        self.register_analyzer(self.analyze_metadata)

    def register_analyzer(self, func: Callable[[str], Dict]):
        self.analyzers.append(func)

    def analyze(self, image_path: str) -> List[Dict]:
        results = []
        for analyzer in self.analyzers:
            try:
                results.append(analyzer(image_path))
            except Exception as e:
                results.append({"analyzer": analyzer.__name__, "error": str(e)})
        return results

    @staticmethod
    def detect_watermark(image_path: str) -> Dict:
        # Placeholder: In reality, use OCR or watermark detection libraries
        # Here, just return a dummy result
        return {"analyzer": "detect_watermark", "found": False, "details": "No watermark detected (placeholder)"}

    @staticmethod
    def analyze_metadata(image_path: str) -> Dict:
        # Placeholder: In reality, use exifread or PIL.Image._getexif()
        try:
            img = Image.open(image_path)
            exif = img.getexif()
            # Example: check for AI-related tags (placeholder logic)
            ai_tags = [k for k, v in exif.items() if "AI" in str(v).upper()]
            is_ai = bool(ai_tags)
            return {"analyzer": "analyze_metadata", "ai_related": is_ai, "details": f"AI tags: {ai_tags}"}
        except Exception as e:
            return {"analyzer": "analyze_metadata", "error": str(e)} 