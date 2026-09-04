import numpy as np
from PIL import Image, ImageDraw

# Calibrated known-good baseline for standard YOLOv11n weights across our 3 deterministic probes
# Probe 1 (Checkerboard): 0.0 | Probe 2 (Concentric circles): 0.455 | Probe 3 (Noise): 0.0
EXPECTED_BEHAVIORAL_VECTOR = np.array([0.0, 0.455, 0.0])


def generate_reference_battery() -> list[Image.Image]:
    """Generates 3 deterministic, memory-resident probe patterns to test network behavior."""
    probes = []

    # Probe 1: High-frequency spatial checkerboard
    img1 = Image.new("RGB", (640, 640), color="black")
    draw1 = ImageDraw.Draw(img1)
    for x in range(0, 640, 64):
        for y in range(0, 640, 64):
            if (x // 64 + y // 64) % 2 == 0:
                draw1.rectangle([x, y, x + 64, y + 64], fill="white")
    probes.append(img1)

    # Probe 2: High-contrast concentric geometric forms
    img2 = Image.new("RGB", (640, 640), color="gray")
    draw2 = ImageDraw.Draw(img2)
    for r in range(20, 300, 40):
        draw2.ellipse([320 - r, 320 - r, 320 + r, 320 + r], outline="black", width=4)
    probes.append(img2)

    # Probe 3: Reproducible pseudo-random noise
    rng = np.random.RandomState(42)
    noise_array = rng.randint(0, 256, (640, 640, 3), dtype=np.uint8)
    img3 = Image.fromarray(noise_array)
    probes.append(img3)

    return probes


def evaluate_behavioral_fingerprint(yolo_model) -> dict:
    """Executes the reference battery and computes output divergence from the expected baseline."""
    probes = generate_reference_battery()
    measured_confidences = []

    for probe in probes:
        results = yolo_model(probe, verbose=False)
        boxes = results[0].boxes
        if len(boxes) > 0:
            top_conf = float(boxes.conf.max().item())
        else:
            top_conf = 0.0
        measured_confidences.append(top_conf)

    measured_vec = np.array(measured_confidences)
    # Mean Absolute Deviation from the reference baseline
    divergence = float(np.mean(np.abs(measured_vec - EXPECTED_BEHAVIORAL_VECTOR)))

    # Acceptance threshold: allows normal floating point variance (< 0.02)
    passed = divergence < 0.02

    return {
        "fingerprint_pass": passed,
        "divergence": round(divergence, 4),
        "measured_vector": [round(x, 3) for x in measured_confidences],
        "access_tier": "WHITE_BOX",
        "stated_limitations": "Evaluates activation stability against standard synthetic probes; adversarial perturbation triggers outside probe domain remain unverified.",
    }