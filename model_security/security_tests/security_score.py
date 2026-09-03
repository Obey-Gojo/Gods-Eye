import json
import sys
from pathlib import Path


# ============================================
# GODSEYE SECURITY SCORE
# ============================================

BASE_DIR = Path(__file__).resolve().parent

behavior_file = BASE_DIR / "behavior_summary.json"
anomaly_file = BASE_DIR / "anomaly_results.json"
output_file = BASE_DIR / "security_results.json"


# ============================================
# LOAD PREVIOUS ANALYSIS RESULTS
# ============================================

with open(behavior_file, "r") as file:
    behavior = json.load(file)

with open(anomaly_file, "r") as file:
    anomaly = json.load(file)


# ============================================
# SELECT MODEL
# ============================================

model_filename = "yolo11n.pt"

if len(sys.argv) > 1:
    model_filename = sys.argv[1]


print("============================================")
print("          GODSEYE SECURITY SCORE")
print("============================================")

print()
print("Model being checked:", model_filename)


# ============================================
# MODEL INTEGRITY VERIFICATION
# ============================================

PROJECT_DIR = BASE_DIR.parent

sys.path.insert(0, str(PROJECT_DIR))

from verify_model import verify_model


model_is_trusted = verify_model(model_filename)


if model_is_trusted:

    integrity_status = "TRUSTED"
    integrity_score = 100

else:

    integrity_status = "TAMPERED"
    integrity_score = 0


# ============================================
# BEHAVIOR ANALYSIS
# ============================================

overall_stability = (
    sum(test["detection_stability"] for test in behavior.values())
    / len(behavior)
)


overall_confidence_change = (
    sum(test["average_confidence_change"] for test in behavior.values())
    / len(behavior)
)


stability_score = overall_stability


confidence_score = max(
    0,
    100 - (overall_confidence_change * 5)
)


behavior_score = (
    stability_score * 0.6
    + confidence_score * 0.4
)


# ============================================
# ANOMALY SCREENING
# ============================================

tests = anomaly["tests"]

normal_count = 0
attention_count = 0
suspicious_count = 0


for test in tests.values():

    status = test["status"]

    if status == "NORMAL":
        normal_count += 1

    elif status == "ATTENTION":
        attention_count += 1

    elif status == "SUSPICIOUS":
        suspicious_count += 1


total_tests = len(tests)


if suspicious_count > 0:

    anomaly_score = 40

elif attention_count > 0:

    anomaly_score = 100 - (
        attention_count / total_tests
    ) * 40

else:

    anomaly_score = 100


# ============================================
# FINAL SECURITY SCORE
# ============================================

final_score = (
    integrity_score * 0.40
    + behavior_score * 0.40
    + anomaly_score * 0.20
)


final_score = round(final_score, 2)


# ============================================
# FINAL STATUS
# ============================================

if not model_is_trusted:

    final_status = "TAMPERED"

elif suspicious_count > 0:

    final_status = "SUSPICIOUS"

elif final_score >= 80:

    final_status = "TRUSTED"

elif final_score >= 60:

    final_status = "ATTENTION"

else:

    final_status = "HIGH RISK"


# ============================================
# DISPLAY RESULTS
# ============================================

print()

print("MODEL INTEGRITY")
print("--------------------------------------------")
print("SHA-256 Status :", integrity_status)
print("Integrity Score:", integrity_score, "/ 100")


print()

print("BEHAVIOR ANALYSIS")
print("--------------------------------------------")
print(
    "Detection Stability :",
    round(overall_stability, 2),
    "%"
)

print(
    "Average Confidence Change :",
    round(overall_confidence_change, 2),
    "%"
)

print(
    "Behavior Score :",
    round(behavior_score, 2),
    "/ 100"
)


print()

print("ANOMALY SCREENING")
print("--------------------------------------------")

print("Normal Tests     :", normal_count)
print("Attention Tests  :", attention_count)
print("Suspicious Tests :", suspicious_count)

print(
    "Anomaly Score    :",
    round(anomaly_score, 2),
    "/ 100"
)


print()

print("============================================")
print("        FINAL SECURITY ASSESSMENT")
print("============================================")

print()

print(
    "Security Score:",
    final_score,
    "/ 100"
)

print(
    "Final Status  :",
    final_status
)


# ============================================
# SAVE RESULTS
# ============================================

security_results = {

    "model": model_filename,

    "model_integrity": {

        "status": integrity_status,

        "score": integrity_score
    },

    "behavior": {

        "detection_stability":
            round(overall_stability, 2),

        "average_confidence_change":
            round(overall_confidence_change, 2),

        "score":
            round(behavior_score, 2)
    },

    "anomaly_screening": {

        "normal_tests":
            normal_count,

        "attention_tests":
            attention_count,

        "suspicious_tests":
            suspicious_count,

        "score":
            round(anomaly_score, 2)
    },

    "final_security_score":
        final_score,

    "final_status":
        final_status
}


with open(output_file, "w") as file:

    json.dump(
        security_results,
        file,
        indent=4
    )


print()

print("Security results saved to:")

print(output_file)

print()

print("============================================")
print("          SECURITY SCAN COMPLETE")
print("============================================")