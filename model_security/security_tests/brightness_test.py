from PIL import Image, ImageEnhance
from pathlib import Path

# Find the model_security folder
project_folder = Path(__file__).resolve().parent.parent

# Original test image
image_path = project_folder / "test_car_1.jpeg"

image = Image.open(image_path)

# Increase brightness slightly
enhancer = ImageEnhance.Brightness(image)
bright_image = enhancer.enhance(1.2)

# Save inside security_tests
output_path = Path(__file__).resolve().parent / "bright_test.jpeg"
bright_image.save(output_path)

print("Brightness test image created successfully.")
print("Saved as:", output_path)