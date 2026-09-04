import io
import json
import os
import time
import requests
from PIL import Image

API_URL = "http://127.0.0.1:8000"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
UPLOADS_DIR = os.path.join(ROOT_DIR, "backend", "uploads")


def get_target_vehicle_image() -> tuple[str, Image.Image]:
    """Finds and loads a verified vehicle image."""
    priority_names = ["images (3).jpg", "images (4).jpg", "download (1).jpg"]
    for name in priority_names:
        p = os.path.join(UPLOADS_DIR, name)
        if os.path.exists(p):
            return name, Image.open(p).convert("RGB")

    for fname in os.listdir(UPLOADS_DIR):
        if fname.lower().endswith((".jpg", ".jpeg", ".png")) and not fname.startswith("asset_"):
            p = os.path.join(UPLOADS_DIR, fname)
            return fname, Image.open(p).convert("RGB")

    raise FileNotFoundError("No vehicle image found in backend/uploads.")


def image_to_bytes_with_nonce(img: Image.Image, nonce: int = 0) -> bytes:
    """Encodes JPEG bytes with an embedded comment marker to produce a unique SHA-256."""
    buf = io.BytesIO()
    if nonce == 0:
        img.save(buf, format="JPEG", quality=95)
    else:
        # Modifying a metadata comment creates a distinct cryptographic hash
        # without changing pixel features or pHash structure
        img.save(buf, format="JPEG", quality=95, comment=f"nonce_{nonce}_{time.time()}".encode())
    return buf.getvalue()


def run_test_case(
    name: str,
    file_name: str,
    file_bytes: bytes,
    contributor: str,
    poison: bool = False,
    backdoor: bool = False,
    tamper: bool = False,
):
    print(f"\n=======================================================")
    print(f"RUNNING: {name}")
    print(f"=======================================================")

    files = {"file": (file_name, file_bytes, "image/jpeg")}
    data = {
        "contributor": contributor,
        "simulate_poison": poison,
        "simulate_backdoor": backdoor,
        "simulate_tamper": tamper,
    }

    try:
        t0 = time.time()
        res = requests.post(f"{API_URL}/process-pipeline", files=files, data=data)
        elapsed = round((time.time() - t0) * 1000, 1)

        if res.status_code != 200:
            print(f"[FAIL] HTTP Error {res.status_code}: {res.text}")
            return False

        payload = res.json()
        print(f"Status:       {payload.get('status')}")
        print(f"Trusted:      {payload.get('is_trusted')}")
        print(f"Prediction:   {payload.get('prediction')} ({payload.get('confidence')})")
        print(f"Tx Hash:      {payload.get('blockchain_tx') or 'NONE (REJECTED)'}")
        print(f"Checks:       {json.dumps(payload.get('checks'))}")
        print(f"Detail:       {payload.get('message')}")
        print(f"Latency:      {elapsed} ms")
        return payload
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return None


def main():
    print("Initializing God's Eye Targeted Adversarial Suite...")
    target_name, target_img = get_target_vehicle_image()
    print(f"[+] Loaded vehicle reference: {target_name}")

    session_id = int(time.time())
    primary_agency = f"Traffic Patrol {session_id}"

    # 1. Baseline Authentic Asset (Expected: VERIFIED)
    raw_bytes = image_to_bytes_with_nonce(target_img, nonce=0)
    run_test_case(
        "1. Baseline Authentic Asset (Expected: VERIFIED)",
        f"fresh_{session_id}.jpg",
        raw_bytes,
        contributor=primary_agency,
    )

    # 2. Duplicate Flooding (Expected: DUPLICATE ASSET)
    run_test_case(
        "2. Duplicate Flooding Attack (Expected: DUPLICATE ASSET)",
        f"fresh_{session_id}.jpg",
        raw_bytes,
        contributor=primary_agency,
    )

    # 3. Cross-Entity Plagiarism (Expected: PLAGIARISM ALERT)
    run_test_case(
        "3. Cross-Entity Plagiarism (Expected: PLAGIARISM ALERT)",
        f"fresh_{session_id}.jpg",
        raw_bytes,
        contributor="Rival Traffic Entity",
    )

    # 4. Data Poisoning (Expected: DATA POISONED)
    # Uses a new contributor so it tests poisoning directly
    run_test_case(
        "4. Data Poisoning / Patch Injection (Expected: DATA POISONED)",
        f"poison_{session_id}.jpg",
        raw_bytes,
        contributor=primary_agency,
        poison=True,
    )

    # 5. Model Weight Attestation Breach (Expected: MODEL COMPROMISED)
    run_test_case(
        "5. Weight Attestation Breach (Expected: MODEL COMPROMISED)",
        f"backdoor_{session_id}.jpg",
        raw_bytes,
        contributor=primary_agency,
        backdoor=True,
    )

    # 6. Output Tampering / Interception (Expected: INFERENCE TAMPERED)
    run_test_case(
        "6. Execution Output Tampering (Expected: INFERENCE TAMPERED)",
        f"tamper_{session_id}.jpg",
        raw_bytes,
        contributor=primary_agency,
        tamper=True,
    )


if __name__ == "__main__":
    main()