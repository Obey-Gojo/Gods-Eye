import io
import cv2
import numpy as np
from PIL import Image


class SpatialDenoisingDefense:
    """
    Adaptive Forensic Spatial Denoising Engine:
    1. Measures Laplacian variance to quantify high-frequency noise density.
    2. Dynamically scales kernel size based on input resolution.
    3. Combines median filtering with bilateral edge-preserving smoothing.
    4. Emits structural metrics and sanitized bytes for downstream YOLOv11 inference.
    """
    def __init__(self, high_freq_threshold: float = 380.0):
        self.high_freq_threshold = high_freq_threshold

    def analyze_and_sanitize(self, img_bytes: bytes) -> dict:
        nparr = np.frombuffer(img_bytes, np.uint8)
        bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if bgr is None:
            return {
                "defense_applied": False,
                "residual_energy": 0.0,
                "sanitized_bytes": img_bytes,
                "status": "UNPROCESSABLE_IMAGE",
                "high_freq_energy": 0.0,
                "residual_delta": 0.0,
            }

        h, w = bgr.shape[:2]

        # 1. High-Frequency Laplacian Variance
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        high_freq_energy = float(laplacian.var())

        # 2. Dynamic Kernel Sizing
        ksize = 3 if min(h, w) <= 450 else 5

        # Median filter to eliminate isolated high-gradient pixel spikes
        median_filtered = cv2.medianBlur(bgr, ksize)

        # Bilateral filter to preserve edge transitions along vehicle silhouettes
        sanitized = cv2.bilateralFilter(median_filtered, d=5, sigmaColor=35, sigmaSpace=35)

        # 3. Residual Energy Delta
        residual_diff = cv2.absdiff(bgr, sanitized)
        mean_residual_delta = float(np.mean(residual_diff))

        perturbation_detected = (
            high_freq_energy > self.high_freq_threshold or mean_residual_delta > 8.0
        )

        _, buffer = cv2.imencode(".jpg", sanitized, [cv2.IMWRITE_JPEG_QUALITY, 95])
        sanitized_bytes = buffer.tobytes()

        return {
            "defense_applied": perturbation_detected,
            "high_freq_energy": round(high_freq_energy, 2),
            "residual_delta": round(mean_residual_delta, 2),
            "sanitized_bytes": sanitized_bytes if perturbation_detected else img_bytes,
            "status": "PERTURBATION_NEUTRALIZED" if perturbation_detected else "NOMINAL_SPECTRUM",
        }


spatial_defense = SpatialDenoisingDefense()