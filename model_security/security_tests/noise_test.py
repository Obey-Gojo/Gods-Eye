from PIL import Image
import numpy as np
from pathlib import Path

# Find the main project folder
project_folder = Path(__file__).resolve().parent.parent

# Original image
image_path = project_folder / "test_car_1.jpeg"

# Open image
image = Image.open(image_path).convert("RGB")

# Convert image to a NumPy array
image_array = np.array(image).astype(np.int16)

# Generate small random visual noise
noise = np.random.normal(
    loc=0,
    scale=8,
    size=image_array.shape
)

# Add noise to the image
noisy_image = image_array + noise

# Keep pixel values between 0 and 255
noisy_image = np.clip(noisy_image, 0, 255)

# Convert back to an image
noisy_image = noisy_image.astype(np.uint8)

# Save the noisy image
output_path = Path(__file__).resolve().parent / "noise_test.jpeg"

Image.fromarray(noisy_image).save(
    output_path,
    "JPEG",
    quality=95
)

print("================================")
print("     NOISE TEST IMAGE")
print("================================")
print("Noise level: small")
print("Noise standard deviation: 8")
print("Saved as:", output_path)