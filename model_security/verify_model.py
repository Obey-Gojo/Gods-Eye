import hashlib
import sys
from pathlib import Path

# ============================================
# MODEL VERIFICATION
# ============================================

PROJECT_DIR = Path(__file__).resolve().parent
ROOT_DIR = PROJECT_DIR.parent
DEFAULT_BACKEND_MODEL = ROOT_DIR / "backend" / "models" / "yolo11n.pt"

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


def verify_model(target_model="yolo11n.pt"):
    """Verify the model against the trusted SHA-256 hash."""
    
    # 1. Check direct path or path relative to CLI execution
    candidate = Path(target_model)
    if candidate.exists() and candidate.is_file():
        model_path = candidate
    # 2. Check in backend/models/ (shared app path)
    elif (ROOT_DIR / "backend" / "models" / target_model).exists():
        model_path = ROOT_DIR / "backend" / "models" / target_model
    # 3. Check inside model_security/ (local folder)
    elif (PROJECT_DIR / target_model).exists():
        model_path = PROJECT_DIR / target_model
    # 4. Fallback to default backend model
    elif DEFAULT_BACKEND_MODEL.exists():
        model_path = DEFAULT_BACKEND_MODEL
    else:
        print()
        print("ERROR: Model file not found!")
        print("Checked paths:")
        print(f" - {PROJECT_DIR / target_model}")
        print(f" - {ROOT_DIR / 'backend' / 'models' / target_model}")
        return False

    current_hash = calculate_hash(model_path)

    print()
    print("=================================")
    print("       MODEL VERIFICATION")
    print("=================================")
    print("Target File :", model_path.name)
    print("Resolved Path:", model_path)
    print()
    print("Trusted Hash:")
    print(TRUSTED_HASH)
    print()
    print("Current Hash:")
    print(current_hash)
    print()

    if current_hash.lower() == TRUSTED_HASH.lower():
        print("STATUS: TRUSTED ✅")
        print("Model integrity verified.")
        return True
    else:
        print("STATUS: TAMPERED ❌")
        print("WARNING: Model has been modified!")
        return False


# ============================================
# COMMAND LINE SUPPORT
# ============================================

if __name__ == "__main__":
    model_arg = "yolo11n.pt"
    if len(sys.argv) > 1:
        model_arg = sys.argv[1]

    verify_model(model_arg)