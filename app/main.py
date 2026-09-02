from app.utils.detector import ObjectDetector
from app.integrity import analyze_integrity
import json


def main():

    image_path = "test_images/car.jpg"
    image_id = "IMG001"

    # -------------------------
    # Computer Vision
    # -------------------------

    detector = ObjectDetector(
        model_path="app/models/yolo11n.pt",
        model_id="vehicle_detector",
        model_version="1.0"
    )

    cv_result = detector.detect(
        image_path=image_path,
        image_id=image_id
    )

    print("\n=== COMPUTER VISION RESULT ===")

    print(json.dumps(cv_result, indent=4))

    # -------------------------
    # Image Integrity
    # -------------------------

    result = analyze_integrity(image_path)

    print("\n=== IMAGE INTEGRITY ===")
    print(f"Integrity Score: {result['score']}/100")

    print("\nImage Metrics:")

    for key, value in result["metrics"].items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()