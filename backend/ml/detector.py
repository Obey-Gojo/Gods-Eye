import hashlib
import os
from typing import Any, Dict, List
from ultralytics import YOLO


class ObjectDetector:
    def __init__(self, model_path: str, model_id: str = "yolo11n_vehicle_detector", model_version: str = "1.0"):
        self.model_path = model_path
        self.model_id = model_id
        self.model_version = model_version

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"YOLO model weights file not found at: {model_path}")

        # Compute authentic cryptographic SHA-256 baseline of weights
        with open(model_path, "rb") as f:
            self.model_hash = hashlib.sha256(f.read()).hexdigest()

        # Load weights into Ultralytics YOLO runtime
        self.model = YOLO(model_path)

        # Vehicle class mappings based on standard COCO dataset indices
        self.vehicle_classes = {
            2: "car",
            3: "motorcycle",
            5: "bus",
            7: "truck",
        }

    def detect(self, image_path: str, image_id: str = "IMG_000") -> Dict[str, Any]:
        results = self.model(image_path, verbose=False)
        detections: List[Dict[str, Any]] = []

        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls_id = int(box.cls[0].item())
                confidence = float(box.conf[0].item())
                xyxy = box.xyxy[0].tolist()

                # Filter strictly for vehicle domain
                if cls_id in self.vehicle_classes:
                    detections.append({
                        "class": self.vehicle_classes[cls_id],
                        "class_id": cls_id,
                        "confidence": confidence,
                        "bbox": xyxy,
                    })

        return {
            "image_id": image_id,
            "model_id": self.model_id,
            "model_version": self.model_version,
            "model_hash": self.model_hash,
            "detections": detections,
        }