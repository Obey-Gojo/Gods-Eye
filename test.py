from integrity import calculate_hash
import json
import os
from datetime import datetime

IMAGE_PATH = "images/car.jpg"
DATABASE_FILE = "image_records.json"


def load_records():
    if not os.path.exists(DATABASE_FILE):
        return []

    with open(DATABASE_FILE, "r") as file:
        return json.load(file)


def register_image():
    contributor = input("Enter contributor name: ")

    current_hash = calculate_hash(IMAGE_PATH)
    records = load_records()

    # Check duplicate
    for record in records:
        if record["hash"] == current_hash:
            print("\n⚠️ DUPLICATE IMAGE DETECTED!")
            print("Already registered by:", record["contributor"])
            return

    image_id = f"IMG{len(records) + 1:03d}"

    record = {
        "image_id": image_id,
        "filename": os.path.basename(IMAGE_PATH),
        "contributor": contributor,
        "timestamp": datetime.now().isoformat(),
        "hash": current_hash
    }

    records.append(record)

    with open(DATABASE_FILE, "w") as file:
        json.dump(records, file, indent=4)

    print("\n✅ IMAGE REGISTERED")
    print("Image ID:", image_id)
    print("Hash:", current_hash)


def verify_image():
    records = load_records()

    if not records:
        print("No registered images found.")
        return

    image_id = input("Enter Image ID to verify: ")

    record = None

    for item in records:
        if item["image_id"] == image_id:
            record = item
            break

    if record is None:
        print("❌ Image ID not found.")
        return

    current_hash = calculate_hash(IMAGE_PATH)

    print("\nOriginal Hash:")
    print(record["hash"])

    print("\nCurrent Hash:")
    print(current_hash)

    if current_hash == record["hash"]:
        print("\n✅ IMAGE IS TRUSTED")
        print("No tampering detected.")
    else:
        print("\n❌ TAMPERING DETECTED!")
        print("The image is different from the registered version.")


print("\n===== DATA INTEGRITY SYSTEM =====")
print("1. Register Image")
print("2. Verify Image")

choice = input("\nChoose option: ")

if choice == "1":
    register_image()

elif choice == "2":
    verify_image()

else:
    print("Invalid choice.")