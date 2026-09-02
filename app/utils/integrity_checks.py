import cv2
import numpy as np


def analyze_image(image_path):
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    height, width = image.shape[:2]

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Blur score using variance of Laplacian
    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()

    # Brightness
    brightness = float(np.mean(gray))

    # Contrast
    contrast = float(np.std(gray))

    # Edge density
    edges = cv2.Canny(gray, 100, 200)
    edge_density = float(np.mean(edges > 0))

    return {
        "width": width,
        "height": height,
        "blur_score": round(blur_score, 2),
        "brightness": round(brightness, 2),
        "contrast": round(contrast, 2),
        "edge_density": round(edge_density, 4),
    }


def calculate_integrity_score(metrics):
    score = 100

    # Extremely blurry images reduce confidence
    if metrics["blur_score"] < 50:
        score -= 20
    elif metrics["blur_score"] < 100:
        score -= 10

    # Very dark or very bright images
    if metrics["brightness"] < 30 or metrics["brightness"] > 225:
        score -= 15

    # Very low contrast
    if metrics["contrast"] < 20:
        score -= 10

    return max(0, min(100, score))