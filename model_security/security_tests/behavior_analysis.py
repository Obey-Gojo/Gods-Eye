from pathlib import Path
import json
import statistics


# ============================================
# GODSEYE MODEL SECURITY
# BEHAVIORAL ANALYSIS
# ============================================

print("============================================")
print("       GODSEYE BEHAVIORAL ANALYSIS")
print("============================================")


# --------------------------------------------
# LOAD RESULTS
# --------------------------------------------

results_file = (
    Path(__file__).resolve().parent /
    "behavior_results.json"
)

with open(results_file, "r", encoding="utf-8") as file:
    all_results = json.load(file)


print()
print("Results file loaded successfully.")
print("Images analyzed:", len(all_results))


# --------------------------------------------
# TEST TYPES
# --------------------------------------------

tests = [
    "brightness",
    "resize",
    "compression",
    "noise"
]


# --------------------------------------------
# STORAGE
# --------------------------------------------

summary = {}


# --------------------------------------------
# ANALYZE EACH TEST
# --------------------------------------------

for test_name in tests:

    print()
    print("============================================")
    print(test_name.upper(), "ANALYSIS")
    print("============================================")

    confidence_changes = []

    images_with_detection_change = 0
    images_compared = 0

    for image_name, image_data in all_results.items():

        original = image_data["original"]
        modified = image_data[test_name]

        # ------------------------------------
        # CASE 1:
        # Both have no detections
        # ------------------------------------

        if not original and not modified:
            continue

        # ------------------------------------
        # CASE 2:
        # Detection appeared/disappeared
        # ------------------------------------

        original_classes = set(original.keys())
        modified_classes = set(modified.keys())

        if original_classes != modified_classes:

            images_with_detection_change += 1

        # ------------------------------------
        # Compare classes present in ORIGINAL
        # ------------------------------------

        common_classes = (
            original_classes &
            modified_classes
        )

        for class_name in common_classes:

            original_confidence = original[class_name]
            modified_confidence = modified[class_name]

            absolute_change = abs(
                modified_confidence -
                original_confidence
            )

            # Percentage change relative to
            # the original confidence
            if original_confidence > 0:

                percentage_change = (
                    absolute_change /
                    original_confidence
                ) * 100

                confidence_changes.append(
                    percentage_change
                )

        images_compared += 1


    # ----------------------------------------
    # CALCULATE STATISTICS
    # ----------------------------------------

    if confidence_changes:

        average_change = statistics.mean(
            confidence_changes
        )

        median_change = statistics.median(
            confidence_changes
        )

        maximum_change = max(
            confidence_changes
        )

    else:

        average_change = 0
        median_change = 0
        maximum_change = 0


    # Detection stability
    if images_compared > 0:

        detection_stability = (
            1 -
            (
                images_with_detection_change /
                images_compared
            )
        ) * 100

    else:

        detection_stability = 100


    # ----------------------------------------
    # STORE
    # ----------------------------------------

    summary[test_name] = {

        "images_compared":
            images_compared,

        "detection_changes":
            images_with_detection_change,

        "detection_stability":
            detection_stability,

        "average_confidence_change":
            average_change,

        "median_confidence_change":
            median_change,

        "maximum_confidence_change":
            maximum_change

    }


    # ----------------------------------------
    # DISPLAY
    # ----------------------------------------

    print()
    print(
        "Images compared:",
        images_compared
    )

    print(
        "Detection changes:",
        images_with_detection_change
    )

    print(
        "Detection stability:",
        round(
            detection_stability,
            2
        ),
        "%"
    )

    print(
        "Average confidence change:",
        round(
            average_change,
            2
        ),
        "%"
    )

    print(
        "Median confidence change:",
        round(
            median_change,
            2
        ),
        "%"
    )

    print(
        "Maximum confidence change:",
        round(
            maximum_change,
            2
        ),
        "%"
    )


# ============================================
# OVERALL ANALYSIS
# ============================================

print()
print("============================================")
print("          OVERALL BEHAVIOR")
print("============================================")


all_average_changes = []

all_detection_stabilities = []


for test_name in tests:

    result = summary[test_name]

    all_average_changes.append(
        result["average_confidence_change"]
    )

    all_detection_stabilities.append(
        result["detection_stability"]
    )


overall_average_change = statistics.mean(
    all_average_changes
)

overall_detection_stability = statistics.mean(
    all_detection_stabilities
)


print()
print(
    "Overall detection stability:",
    round(
        overall_detection_stability,
        2
    ),
    "%"
)

print(
    "Overall average confidence change:",
    round(
        overall_average_change,
        2
    ),
    "%"
)


# ============================================
# BEHAVIORAL ASSESSMENT
# ============================================

print()
print("============================================")
print("       SECURITY ASSESSMENT")
print("============================================")


# These are screening thresholds for this
# prototype. They are NOT universal security
# standards.

if (
    overall_detection_stability >= 90
    and overall_average_change < 10
):

    status = "NORMAL"

elif (
    overall_detection_stability >= 75
    and overall_average_change < 20
):

    status = "ATTENTION"

else:

    status = "SUSPICIOUS"


print()
print("Behavioral Status:", status)


if status == "NORMAL":

    print()
    print(
        "The model showed generally stable "
        "behavior across the controlled "
        "image transformations."
    )

elif status == "ATTENTION":

    print()
    print(
        "Some behavioral changes were observed."
    )

    print(
        "Further testing is recommended."
    )

else:

    print()
    print(
        "Significant behavioral changes were "
        "observed."
    )

    print(
        "Further security investigation is "
        "recommended."
    )


# ============================================
# SAVE SUMMARY
# ============================================

summary_file = (
    Path(__file__).resolve().parent /
    "behavior_summary.json"
)

with open(
    summary_file,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        summary,
        file,
        indent=4
    )


print()
print("============================================")
print("       ANALYSIS COMPLETE")
print("============================================")

print()
print("Detailed summary saved to:")

print(summary_file)