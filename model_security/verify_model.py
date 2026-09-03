import hashlib
import sys
from pathlib import Path


# ============================================
# MODEL VERIFICATION
# ============================================

PROJECT_DIR = Path(__file__).resolve().parent


# Trusted SHA-256 hash provided by Member 2
TRUSTED_HASH = (
    "0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1"
)


def calculate_hash(model_path):
    """Calculate SHA-256 hash of a model file."""

    sha256 = hashlib.sha256()

    with open(model_path, "rb") as file:
        while True:
            data = file.read(4096)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()


def verify_model(model_filename="yolo11n.pt"):
    """Verify the model against the trusted SHA-256 hash."""

    model_path = PROJECT_DIR / model_filename

    if not model_path.exists():
        print()
        print("ERROR: Model file not found!")
        print("File:", model_path)
        return False

    current_hash = calculate_hash(model_path)

    print()
    print("=================================")
    print("       MODEL VERIFICATION")
    print("=================================")

    print("Model:", model_filename)

    print()
    print("Trusted Hash:")
    print(TRUSTED_HASH)

    print()
    print("Current Hash:")
    print(current_hash)

    print()

    if current_hash == TRUSTED_HASH:

        print("STATUS: TRUSTED")
        print("Model integrity verified.")

        return True

    else:

        print("STATUS: TAMPERED")
        print("WARNING: Model has been modified!")

        return False


# ============================================
# COMMAND LINE SUPPORT
# ============================================

if __name__ == "__main__":

    # Default model
    model_filename = "yolo11n.pt"

    # If another model was provided in the command
    if len(sys.argv) > 1:
        model_filename = sys.argv[1]

    verify_model(model_filename)