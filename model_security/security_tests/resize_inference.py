from ultralytics import YOLO

# Load the trusted model
model = YOLO("../yolo11n.pt")

# Run detection on resized image
results = model("security_tests/resize_test.jpeg")

print("================================")
print("      RESIZE SECURITY TEST")
print("================================")

for result in results:

    if result.boxes is None or len(result.boxes) == 0:
        print("No objects detected.")
        continue

    for box in result.boxes:

        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        class_name = model.names[class_id]

        print()
        print("Class:", class_name)
        print("Confidence:", round(confidence, 4))
        print("Bounding Box:", box.xyxy[0].tolist())