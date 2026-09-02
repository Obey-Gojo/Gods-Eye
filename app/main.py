from app.utils.detector import ObjectDetector
import json
from pathlib import Path


def main():

    detector = ObjectDetector(
        model_path="app/models/yolo11n.pt",
        model_id="vehicle_detector",
        model_version="1.0"
    )

    test_folder = Path("test_images")

    image_files = [
        "car.jpg",
        "truck.jpg",
        "bus.jpg",
        "motorcycle.jpg",
        "no_vehicle.jpg"
    ]

    for filename in image_files:

        image_path = test_folder / filename

        print("\n" + "=" * 60)
        print(f"TEST IMAGE: {filename}")
        print("=" * 60)

        if not image_path.exists():
            print("ERROR: Image not found!")
            continue

        result = detector.detect(
            image_path=str(image_path),
            image_id=filename
        )

        print(json.dumps(result, indent=4))


if __name__ == "__main__":
    main()