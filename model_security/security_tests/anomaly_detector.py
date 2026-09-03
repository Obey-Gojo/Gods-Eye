import json
from pathlib import Path


# ============================================
# GODSEYE ANOMALY DETECTOR
# ============================================

BASE_DIR = Path(__file__).resolve().parent

summary_file = BASE_DIR / "behavior_summary.json"
output_file = BASE_DIR / "anomaly_results.json"


# --------------------------------------------
# Load behavioral results
# --------------------------------------------

with open(summary_file, "r") as file:
    data = json.load(file)

print("============================================")
print("       GODSEYE ANOMALY DETECTOR")
print("============================================")

print()
print("Behavior summary loaded successfully.")


# --------------------------------------------
# Screening thresholds
# --------------------------------------------

# These are engineering screening thresholds
# for our prototype. They are NOT universal
# backdoor detection standards.

STABILITY_NORMAL = 90.0
STABILITY_ATTENTION = 75.0

CONFIDENCE_NORMAL = 10.0
CONFIDENCE_ATTENTION = 20.0

MAX_CHANGE_ATTENTION = 30.0
MAX_CHANGE_SUSPICIOUS = 50.0


# --------------------------------------------
# Analyze each transformation
# --------------------------------------------

results = {}


for test_name, metrics in data.items():

    stability = metrics["detection_stability"]
    average_change = metrics["average_confidence_change"]
    maximum_change = metrics["maximum_confidence_change"]

    anomaly_flags = []

    # Detection stability
    if stability < STABILITY_ATTENTION:
        anomaly_flags.append("LOW_DETECTION_STABILITY")

    elif stability < STABILITY_NORMAL:
        anomaly_flags.append("MODERATE_DETECTION_CHANGE")

    # Average confidence change
    if average_change >= CONFIDENCE_ATTENTION:
        anomaly_flags.append("HIGH_AVERAGE_CONFIDENCE_CHANGE")

    elif average_change >= CONFIDENCE_NORMAL:
        anomaly_flags.append("ELEVATED_AVERAGE_CONFIDENCE_CHANGE")

    # Maximum confidence change
    if maximum_change >= MAX_CHANGE_SUSPICIOUS:
        anomaly_flags.append("VERY_HIGH_SINGLE_CASE_CHANGE")

    elif maximum_change >= MAX_CHANGE_ATTENTION:
        anomaly_flags.append("HIGH_SINGLE_CASE_CHANGE")

    # ----------------------------------------
    # Determine status
    # ----------------------------------------

    if (
        stability < STABILITY_ATTENTION
        or average_change >= CONFIDENCE_ATTENTION
        or maximum_change >= MAX_CHANGE_SUSPICIOUS
    ):
        status = "SUSPICIOUS"

    elif (
        stability < STABILITY_NORMAL
        or average_change >= CONFIDENCE_NORMAL
        or maximum_change >= MAX_CHANGE_ATTENTION
    ):
        status = "ATTENTION"

    else:
        status = "NORMAL"

    results[test_name] = {
        "detection_stability": stability,
        "average_confidence_change": round(average_change, 2),
        "maximum_confidence_change": round(maximum_change, 2),
        "status": status,
        "anomaly_flags": anomaly_flags
    }


# --------------------------------------------
# Print results
# --------------------------------------------

for test_name, result in results.items():

    print()
    print("--------------------------------------------")
    print(test_name.upper())
    print("--------------------------------------------")

    print(
        "Detection stability:",
        result["detection_stability"],
        "%"
    )

    print(
        "Average confidence change:",
        result["average_confidence_change"],
        "%"
    )

    print(
        "Maximum confidence change:",
        result["maximum_confidence_change"],
        "%"
    )

    print(
        "Status:",
        result["status"]
    )

    if result["anomaly_flags"]:

        print("Flags:")

        for flag in result["anomaly_flags"]:
            print(" -", flag)

    else:

        print("Flags: None")


# --------------------------------------------
# Overall assessment
# --------------------------------------------

statuses = [
    result["status"]
    for result in results.values()
]

if "SUSPICIOUS" in statuses:

    overall_status = "SUSPICIOUS"

elif "ATTENTION" in statuses:

    overall_status = "ATTENTION"

else:

    overall_status = "NORMAL"


# --------------------------------------------
# Save results
# --------------------------------------------

output_data = {
    "overall_status": overall_status,
    "tests": results
}


with open(output_file, "w") as file:

    json.dump(
        output_data,
        file,
        indent=4
    )


# --------------------------------------------
# Final output
# --------------------------------------------

print()
print("============================================")
print("        OVERALL ANOMALY ASSESSMENT")
print("============================================")

print()
print("Overall Status:", overall_status)

print()
print("Results saved to:")
print(output_file)

print()
print("============================================")
print("          ANALYSIS COMPLETE")
print("============================================")