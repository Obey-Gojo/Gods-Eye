from app.utils.integrity_checks import (
    analyze_image,
    calculate_integrity_score,
)


def analyze_integrity(image_path):
    metrics = analyze_image(image_path)

    score = calculate_integrity_score(metrics)

    return {
        "score": score,
        "metrics": metrics,
    }