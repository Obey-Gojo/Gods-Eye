from ultralytics import YOLO
from pathlib import Path
import json


# ============================================
# STAGE 2B - MULTI-IMAGE YOLO ANALYSIS
# ============================================

print("============================================")
print("     STAGE 2B: YOLO SECURITY ANALYSIS")
print("============================================")


# --------------------------------------------
# PATHS
# --------------------------------------------

project_folder = Path(__file__).resolve().parent.parent

image_folder = Path(__file__).resolve().parent / "test_images"
modified_folder = Path(__file__).resolve().parent / "modified_images"

results_file = (
    Path(__file__).resolve().parent /
    "behavior_results.json"
)


# --------------------------------------------
# LOAD MODEL
# --------------------------------------------

model_path = project_folder / "yolo11n.pt"

print()
print("Loading YOLO model...")

model = YOLO(model_path)

print("YOLO model loaded successfully.")


# --------------------------------------------
# FIND ORIGINAL IMAGES
# --------------------------------------------

images = sorted(image_folder.glob("*.jpeg"))

print()
print("Original images found:", len(images))


# --------------------------------------------
# FUNCTION TO RUN YOLO
# --------------------------------------------

def get_detections(image_path):

    results = model(
        str(image_path),
        verbose=False
    )

    detections = {}

    for result in results:

        if result.boxes is None:
            continue

        for box in result.boxes:

            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            class_name = model.names[class_id]

            # Keep highest confidence for each class
            if (
                class_name not in detections
                or confidence > detections[class_name]
            ):
                detections[class_name] = confidence

    return detections


# --------------------------------------------
# STORAGE FOR ALL RESULTS
# --------------------------------------------

all_results = {}


# --------------------------------------------
# TEST ALL IMAGES
# --------------------------------------------

for image_path in images:

    image_name = image_path.stem

    print()
    print("============================================")
    print("IMAGE:", image_path.name)
    print("============================================")


    # ----------------------------------------
    # ORIGINAL
    # ----------------------------------------

    original_results = get_detections(image_path)

    print()
    print("ORIGINAL:")

    if original_results:

        for class_name, confidence in original_results.items():

            print(
                " ",
                class_name,
                "→",
                round(confidence, 4)
            )

    else:

        print("  No objects detected.")


    # ----------------------------------------
    # BRIGHTNESS
    # ----------------------------------------

    brightness_path = (
        modified_folder /
        f"{image_name}_brightness.jpeg"
    )

    brightness_results = get_detections(
        brightness_path
    )

    print()
    print("BRIGHTNESS:")

    if brightness_results:

        for class_name, confidence in brightness_results.items():

            print(
                " ",
                class_name,
                "→",
                round(confidence, 4)
            )

    else:

        print("  No objects detected.")


    # ----------------------------------------
    # RESIZE
    # ----------------------------------------

    resize_path = (
        modified_folder /
        f"{image_name}_resize.jpeg"
    )

    resize_results = get_detections(
        resize_path
    )

    print()
    print("RESIZE:")

    if resize_results:

        for class_name, confidence in resize_results.items():

            print(
                " ",
                class_name,
                "→",
                round(confidence, 4)
            )

    else:

        print("  No objects detected.")


    # ----------------------------------------
    # COMPRESSION
    # ----------------------------------------

    compression_path = (
        modified_folder /
        f"{image_name}_compression.jpeg"
    )

    compression_results = get_detections(
        compression_path
    )

    print()
    print("COMPRESSION:")

    if compression_results:

        for class_name, confidence in compression_results.items():

            print(
                " ",
                class_name,
                "→",
                round(confidence, 4)
            )

    else:

        print("  No objects detected.")


    # ----------------------------------------
    # NOISE
    # ----------------------------------------

    noise_path = (
        modified_folder /
        f"{image_name}_noise.jpeg"
    )

    noise_results = get_detections(
        noise_path
    )

    print()
    print("NOISE:")

    if noise_results:

        for class_name, confidence in noise_results.items():

            print(
                " ",
                class_name,
                "→",
                round(confidence, 4)
            )

    else:

        print("  No objects detected.")


    # ----------------------------------------
    # STORE RESULTS
    # ----------------------------------------

    all_results[image_name] = {

        "original": original_results,

        "brightness": brightness_results,

        "resize": resize_results,

        "compression": compression_results,

        "noise": noise_results

    }


# --------------------------------------------
# SAVE RESULTS
# --------------------------------------------

with open(
    results_file,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        all_results,
        file,
        indent=4
    )


# --------------------------------------------
# COMPLETE
# --------------------------------------------

print()
print("============================================")
print("       YOLO SECURITY ANALYSIS COMPLETE")
print("============================================")

print()
print("Images tested:", len(images))
print("Original images:", len(images))
print("Modified images:", len(images) * 4)

print()
print("Results saved to:")

print(results_file)

print()
print("All inference tests completed successfully.")