import io
import os
import numpy as np
from PIL import Image
import requests

API_URL = "http://127.0.0.1:8000"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "..", "backend", "uploads")


def inject_adversarial_patch(img: Image.Image) -> bytes:
    """Injects a high-frequency adversarial sticker patch onto the image."""
    arr = np.array(img).copy()
    h, w, _ = arr.shape

    # Bounded adversarial noise patch (e.g. license plate or hood sticker)
    ph, pw = min(64, h // 4), min(64, w // 4)
    y1 = h // 2 - ph // 2
    x1 = w // 2 - pw // 2

    noise_patch = np.random.choice([0, 255], size=(ph, pw, 3), p=[0.5, 0.5]).astype(np.uint8)
    arr[y1:y1 + ph, x1:x1 + pw] = noise_patch

    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, format="JPEG", quality=95)
    return buf.getvalue()


def run_spatial_defense_test():
    candidate_names = [
        "images (3).jpg",
        "looking-for-a-camera-that-can-take-good-car-pictures-v0-6eqjx5scx8sc1.webp",
        "download (1).jpg",
    ]
    target_path = None
    for name in candidate_names:
        p = os.path.join(UPLOADS_DIR, name)
        if os.path.exists(p):
            target_path = p
            break

    if not target_path:
        for fname in os.listdir(UPLOADS_DIR):
            if fname.lower().endswith((".jpg", ".jpeg", ".png", ".webp")) and not fname.startswith("asset_"):
                target_path = os.path.join(UPLOADS_DIR, fname)
                break

    if not target_path:
        print("[!] Error: No target test image found in backend/uploads.")
        return

    print(f"[+] Loaded baseline image for perturbation testing: {os.path.basename(target_path)}")

    with Image.open(target_path).convert("RGB") as img:
        noisy_bytes = inject_adversarial_patch(img)

    print("\n=======================================================")
    print("TESTING: Spatial Denoising Defense & Perturbation Stripping")
    print("=======================================================")

    files = {"file": ("adversarial_patch.jpg", noisy_bytes, "image/jpeg")}
    data = {"contributor": f"Spatial Defense Lab {int(os.times().system)}"}

    resp = requests.post(f"{API_URL}/process-pipeline", files=files, data=data)
    if resp.status_code != 200:
        print(f"[FAIL] HTTP Error {resp.status_code}: {resp.text}")
        return

    payload = resp.json()
    defense = payload.get("spatial_defense", {})

    print(f"Status:          {payload.get('status')}")
    print(f"Prediction:      {payload.get('prediction')} ({payload.get('confidence')})")
    print(f"Defense Applied: {defense.get('applied')}")
    print(f"Spectral State:  {defense.get('status')}")
    print(f"HF Energy Index: {defense.get('high_freq_energy')}")
    print(f"Residual Delta:  {defense.get('residual_delta')}")
    print("=======================================================\n")


if __name__ == "__main__":
    run_spatial_defense_test()