from PIL import Image
from pathlib import Path

# Find the model_security folder
project_folder = Path(__file__).resolve().parent.parent

# Original image
image_path = project_folder / "test_car_1.jpeg"

image = Image.open(image_path)

# Convert to RGB
image = image.convert("RGB")

# Save with reduced JPEG quality
output_path = Path(__file__).resolve().parent / "compressed_test.jpeg"

image.save(
    output_path,
    "JPEG",
    quality=30
)

print("Compression test image created successfully.")
print("JPEG quality: 30")
print("Saved as:", output_path)