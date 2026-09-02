from ultralytics import YOLO
from pathlib import Path
import hashlib
from datetime import datetime, timezone


class ObjectDetector:

    def __init__(
        self,
        model_path="app/models/yolo11n.pt",
        model_id="vehicle_detector",
        model_version="1.0"
    ):
        self.model_path = Path(model_path)
        self.model_id = model_id
        self.model_version = model_version

        # Check that model exists
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model not found: {self.model_path}"
            )

        # Load YOLO model
        self.model = YOLO(str(self.model_path))

        # Calculate model fingerprint
        self.model_hash = self.calculate_sha256()

    def calculate_sha256(self):
        """
        Calculate SHA-256 hash of the model file.
        """

        sha256 = hashlib.sha256()

        with open(self.model_path, "rb") as f:
            for block in iter(lambda: f.read(65536), b""):
                sha256.update(block)

        return sha256.hexdigest()

    def detect(self, image_path, image_id):
        """
        Run YOLO detection and return a structured result.
        """

        results = self.model(image_path)

        detections = []

        # COCO vehicle class IDs
        vehicle_classes = {
            2: "car",
            3: "motorcycle",
            5: "bus",
            7: "truck"
        }

        for result in results:

            for box in result.boxes:

                class_id = int(box.cls[0])
                confidence = float(box.conf[0])

                # Only keep vehicles
                if class_id not in vehicle_classes:
                    continue

                detections.append({
                    "class_id": class_id,
                    "class": vehicle_classes[class_id],
                    "confidence": round(confidence, 4),
                    "bbox": [
                        round(float(x), 2)
                        for x in box.xyxy[0]
                    ]
                })

        return {
            "image_id": image_id,
            "model_id": self.model_id,
            "model_version": self.model_version,
            "model_hash": self.model_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "detections": detections
        }