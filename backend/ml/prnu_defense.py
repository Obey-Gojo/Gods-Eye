import io
import cv2
import numpy as np
from PIL import Image
import pywt


class PRNUDetector:
    """
    Forensic Hardware Fingerprint Validator:
    1. Extracts high-frequency sensor noise residual via Wavelet Denoising (db8).
    2. Quantifies spatial cross-channel variance and spectral flatness.
    3. Detects the absence of silicon CMOS/CCD sensor fingerprints typical of diffusion models.
    """
    def __init__(self, min_sensor_variance: float = 1.8, max_flatness_ratio: float = 0.88):
        self.min_sensor_variance = min_sensor_variance
        self.max_flatness_ratio = max_flatness_ratio

    def _extract_wavelet_noise(self, channel: np.ndarray) -> np.ndarray:
        """Extracts high-frequency noise residual using 2D orthogonal Daubechies wavelets."""
        coeffs = pywt.dwt2(channel, "db8")
        LL, (LH, HL, HH) = coeffs

        # Estimate noise variance using Median Absolute Deviation (MAD) of the HH sub-band
        sigma = float(np.median(np.abs(HH))) / 0.6745
        threshold = 3.0 * sigma

        LH_t = pywt.threshold(LH, threshold, mode="soft")
        HL_t = pywt.threshold(HL, threshold, mode="soft")
        HH_t = pywt.threshold(HH, threshold, mode="soft")

        denoised = pywt.idwt2((LL, (LH_t, HL_t, HH_t)), "db8")
        denoised = cv2.resize(denoised, (channel.shape[1], channel.shape[0]))

        noise_residual = channel - denoised
        return noise_residual

    def analyze_sensor_fingerprint(self, img_bytes: bytes) -> dict:
        nparr = np.frombuffer(img_bytes, np.uint8)
        bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if bgr is None:
            return {
                "has_hardware_fingerprint": False,
                "residual_variance": 0.0,
                "spectral_flatness": 1.0,
                "sensor_confidence": 0.0,
                "verdict": "UNREADABLE_IMAGE",
            }

        img_float = bgr.astype(np.float32) / 255.0

        # Extract high-frequency noise residuals across green and blue channels
        residual_g = self._extract_wavelet_noise(img_float[:, :, 1])
        residual_b = self._extract_wavelet_noise(img_float[:, :, 0])

        var_g = float(np.var(residual_g) * 1e4)
        var_b = float(np.var(residual_b) * 1e4)
        mean_var = (var_g + var_b) / 2.0

        fft_g = np.fft.fft2(residual_g)
        psd_g = np.abs(fft_g) ** 2
        geometric_mean = np.exp(np.mean(np.log(psd_g + 1e-12)))
        arithmetic_mean = np.mean(psd_g) + 1e-12
        spectral_flatness = float(geometric_mean / arithmetic_mean)

        has_sensor_noise = (mean_var >= self.min_sensor_variance) and (spectral_flatness < self.max_flatness_ratio)
        score = np.clip((mean_var / 5.0) * (1.0 - spectral_flatness), 0.0, 1.0)

        return {
            "has_hardware_fingerprint": has_sensor_noise,
            "residual_variance": round(mean_var, 3),
            "spectral_flatness": round(spectral_flatness, 3),
            "sensor_confidence": round(float(score) * 100, 1),
            "verdict": "PHYSICAL_CAMERA_SENSOR" if has_sensor_noise else "SYNTHETIC_OR_NO_SENSOR",
        }


prnu_detector = PRNUDetector()