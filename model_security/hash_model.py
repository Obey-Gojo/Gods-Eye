import hashlib

# Model file
model_file = "yolo11n.pt"

# Create SHA-256 hash
sha256 = hashlib.sha256()

with open(model_file, "rb") as f:
    while chunk := f.read(4096):
        sha256.update(chunk)

model_hash = sha256.hexdigest()

print("================================")
print("       MODEL SECURITY")
print("================================")
print("Model:", model_file)
print("SHA-256 Hash:")
print(model_hash)