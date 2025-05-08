from images.classifier import ImageClassifier
import os

image_classifier = ImageClassifier()

output = image_classifier.classify_image(os.path.abspath(os.path.join(os.path.dirname(__file__), 'image.png')))

print(output)

