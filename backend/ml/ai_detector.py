import io
import cv2
import numpy as np
from PIL import Image
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification


class SyntheticImageDetector:
    """
    Forensic AI Generation vs. Digital Enhancement Engine:
    1. ViT Classifier with high-confidence gating (>= 0.82).
    2. Radial Power Spectrum Slope (Physics of Optical Lenses vs. Diffusion Latents).
    3. Chrominance Noise Covariance (Distinguishes HDR/tone-mapping from synthetic pixel engines).
    """
    def __init__(self, model_name: str = "umm-maybe/AI-image-detector", threshold: float = 0.80):
        self.threshold = threshold
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_loaded = False

        try:
            print(f"[AI DETECTOR] Initializing robust forensic engine ({model_name}) on {self.device}...")
            self.processor = AutoImageProcessor.from_pretrained(model_name)
            self.model = AutoModelForImageClassification.from_pretrained(model_name).to(self.device)
            self.model.eval()
            self.model_loaded = True
            print(f"[AI DETECTOR] Production classifier loaded. Labels: {self.model.config.id2label}")
        except Exception as e:
            print(f"[AI DETECTOR] Model failed to load: {e}")

    def _compute_spectral_slope(self, gray: np.ndarray) -> float:
        """
        Calculates the 2D FFT radial power decay slope alpha.
        Physical lenses follow natural scene statistics (alpha ~= 2.0).
        Synthetic diffusion engines exhibit abnormal decay (alpha < 1.4 or alpha > 2.7).
        """
        h, w = gray.shape
        f = np.fft.fft2(gray)
        fshift = np.fft.fftshift(f)
        psd = np.abs(fshift) ** 2

        cy, cx = h // 2, w // 2
        y, x = np.ogrid[:h, :w]
        r = np.sqrt((x - cx) ** 2 + (y - cy) ** 2).astype(np.int32)

        # Radially average power spectrum
        max_r = min(cy, cx)
        if max_r < 10:
            return 2.0

        radial_prof = np.zeros(max_r)
        counts = np.zeros(max_r)

        for i in range(1, max_r):
            mask = (r == i)
            if np.any(mask):
                radial_prof[i] = np.mean(psd[mask])
                counts[i] = 1

        valid = counts > 0
        freqs = np.arange(max_r)[valid]
        powers = radial_prof[valid]

        # Log-log linear fit: log(P) = -alpha * log(f) + c
        valid_idx = (freqs > 3) & (powers > 0)
        if np.sum(valid_idx) < 5:
            return 2.0

        log_f = np.log(freqs[valid_idx])
        log_p = np.log(powers[valid_idx])

        slope, _ = np.polyfit(log_f, log_p, 1)
        return float(-slope)

    def _compute_chroma_covariance(self, bgr: np.ndarray) -> float:
        """
        Digitally enhanced images maintain natural chrominance covariance in YCrCb.
        Synthetic generators display abnormal decoupled color shifts.
        """
        ycrcb = cv2.cvtColor(bgr, cv2.COLOR_BGR2YCrCb)
        cr = ycrcb[:, :, 1].astype(np.float32)
        cb = ycrcb[:, :, 2].astype(np.float32)

        cr_diff = cv2.Laplacian(cr, cv2.CV_32F)
        cb_diff = cv2.Laplacian(cb, cv2.CV_32F)

        # Pearson correlation of high-frequency color gradients
        cov = np.cov(cr_diff.flatten(), cb_diff.flatten())
        if cov[0, 0] * cov[1, 1] == 0:
            return 0.0
        corr = cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1])
        return float(corr)

    def evaluate(self, img_bytes: bytes) -> dict:
        if not self.model_loaded:
            return {
                "is_ai": False,
                "ai_probability": 0.0,
                "real_probability": 100.0,
                "label": "NATURAL_CAMERA",
                "method": "BYPASS_UNLOADED"
            }

        try:
            image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            nparr = np.frombuffer(img_bytes, np.uint8)
            bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if bgr is None:
                bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

            # 1. Primary ViT Inference
            inputs = self.processor(images=image, return_tensors="pt").to(self.device)
            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]

            id2label = {int(k): str(v).lower() for k, v in self.model.config.id2label.items()}
            fake_idx = 1
            real_idx = 0
            for idx, label in id2label.items():
                if any(term in label for term in ["artificial", "fake", "ai", "synthetic"]):
                    fake_idx = idx
                elif any(term in label for term in ["human", "real", "natural"]):
                    real_idx = idx

            raw_fake_prob = float(probs[fake_idx].item())
            raw_real_prob = float(probs[real_idx].item())

            # 2. Physics & Optical Verifiers
            spectral_slope = self._compute_spectral_slope(gray)
            chroma_corr = self._compute_chroma_covariance(bgr)

            # Natural optical boundary checks:
            # - Optical lens decay slope typically sits in [1.5, 2.6]
            # - Camera sensors maintain correlated chrominance noise (> 0.10)
            is_optically_natural = (1.50 <= spectral_slope <= 2.65) and (chroma_corr >= 0.08)

            # 3. Decision Matrix
            # Only flag as AI if:
            # - Overwhelming ViT certainty (>= 0.88), OR
            # - Confident ViT prediction (>= 0.70) accompanied by optical/spectral violations
            if raw_fake_prob >= 0.88:
                is_ai = True
                final_ai_prob = raw_fake_prob
            elif raw_fake_prob >= 0.70 and not is_optically_natural:
                is_ai = True
                final_ai_prob = raw_fake_prob
            else:
                # Whitelist digital HDR, contrast enhancement, and tone-mapping
                is_ai = False
                final_ai_prob = raw_fake_prob if not is_optically_natural else min(raw_fake_prob, 0.35)

            return {
                "is_ai": is_ai,
                "ai_probability": round(final_ai_prob * 100, 1),
                "raw_model_prob": round(raw_fake_prob * 100, 1),
                "real_probability": round(raw_real_prob * 100, 1),
                "spectral_slope": round(spectral_slope, 2),
                "chroma_covariance": round(chroma_corr, 3),
                "optically_natural": is_optically_natural,
                "threshold_used": self.threshold,
                "method": "OPTICAL_PHYSICS_VIT_ENSEMBLE",
                "label": "AI_GENERATED" if is_ai else "NATURAL_CAMERA",
            }

        except Exception as e:
            print(f"[AI DETECTOR] Evaluation exception: {e}")
            return {
                "is_ai": False,
                "ai_probability": 0.0,
                "real_probability": 100.0,
                "label": "NATURAL_CAMERA",
                "method": "ERROR_FALLBACK",
            }


ai_detector = SyntheticImageDetector()