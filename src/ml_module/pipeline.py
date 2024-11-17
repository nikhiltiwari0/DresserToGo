from transformers import pipeline
from PIL import Image
import cv2
import matplotlib.pyplot as plt

class TooManyHumansException(Exception):
    """Custom exception for too many humans detected."""
    pass

# Define a custom pipeline class
class HumanClothesDetectionPipeline:
    def __init__(self):
        # Load the first model for human detection
        self.human_pipe = pipeline("object-detection", model="hustvl/yolos-tiny", accelerator='ort')
        self.clothing_pipe = pipeline("object-detection", model="valentinafeve/yolos-fashionpedia", accelerator='ort')

    def __call__(self, image_path):
        # Step 1: Detect humans
        humans = self.human_pipe(image_path)

        # Filter out detections with low confidence
        human_boxes = [
            detection["box"]
            for detection in humans
            if detection["score"] >= 0.9 and detection["label"] == "person"
        ]
            
        # Count the number of humans detected
        human_count = len(human_boxes)
        if human_count > 2:
            print(f"Too many humans detected: {human_count}")

        # Crop human regions
        box = human_boxes[0]

        # Step 2: Detect clothes within each cropped region
        clothes = self.clothing_pipe(image_path)

        # Combine results
        return box, clothes