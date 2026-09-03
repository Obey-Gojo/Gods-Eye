from PIL import Image
from pathlib import Path

# Find the model_security folder
project_folder = Path(__file__).resolve().parent.parent

# Original image
image_path = project_folder / "test_car_1.jpeg"

image = Image.open(image_path)

# Resize image to 50% of its original dimensions
new_width = image.width // 2
new_height = image.height // 2

resized_image = image.resize((new_width, new_height))

# Save the resized image
output_path = Path(__file__).resolve().parent / "resize_test.jpeg"
resized_image.save(output_path)

print("Resize test image created successfully.")
print("Original size:", image.size)
print("New size:", resized_image.size)
print("Saved as:", output_path)