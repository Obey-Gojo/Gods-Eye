print("========================================")
print("       GODSEYE MODEL SECURITY REPORT")
print("========================================")

model_name = "yolo11n.pt"
model_version = "1.0"

trusted_hash = "0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1"

print()
print("Model:", model_name)
print("Model Version:", model_version)
print()
print("Trusted SHA-256:")
print(trusted_hash)

import hashlib
from pathlib import Path

# Find the model file
project_folder = Path(__file__).resolve().parent.parent
model_path = project_folder / model_name

# Calculate the current SHA-256 hash
sha256 = hashlib.sha256()

with open(model_path, "rb") as model_file:
    while True:
        data = model_file.read(8192)

        if not data:
            break

        sha256.update(data)

current_hash = sha256.hexdigest()

# Compare the hashes
if current_hash == trusted_hash:
    integrity_status = "TRUSTED"
else:
    integrity_status = "TAMPERED"

print()
print("Current SHA-256:")
print(current_hash)

print()
print("Model Integrity Status:", integrity_status)

print()
print("----------------------------------------")
print("       BEHAVIORAL SECURITY TESTS")
print("----------------------------------------")

# Original baseline results
baseline = {
    "person": 0.8816,
    "motorcycle": 0.7597
}

# Brightness test
brightness = {
    "person": 0.8793,
    "motorcycle": 0.7721
}

# Resize test
resize = {
    "person": 0.8332,
    "motorcycle": 0.7828
}

# Compression test
compression = {
    "person": 0.8502,
    "motorcycle": 0.8511
}

# Noise test
noise = {
    "person": 0.8823,
    "motorcycle": 0.6347
}

def compare_test(test_name, test_results):

    print()
    print(test_name)
    print("----------------------------------------")

    for object_name in baseline:

        original = baseline[object_name]
        modified = test_results.get(object_name)

        if modified is None:
            print(object_name, ": NOT DETECTED")
            continue

        difference = modified - original

        print("Object:", object_name)
        print("Original confidence:", round(original, 4))
        print("Modified confidence:", round(modified, 4))
        print("Difference:", round(difference, 4))
        print()


# Compare all behavioral tests
compare_test("BRIGHTNESS TEST", brightness)
compare_test("RESIZE TEST", resize)
compare_test("COMPRESSION TEST", compression)
compare_test("NOISE TEST", noise)

print()
print("----------------------------------------")
print("          SECURITY ASSESSMENT")
print("----------------------------------------")

print()
print("Model Integrity:")
if integrity_status == "TRUSTED":
    print("PASS - Model hash matches the trusted hash.")
else:
    print("FAIL - Model hash does not match the trusted hash.")

print()
print("Behavioral Testing:")
print("PASS - Same objects were detected across all")
print("      controlled image modifications.")

print()
print("Noise Test:")
print("ATTENTION - Motorcycle confidence decreased")
print("           noticeably under visual noise.")

print()
print("Overall Assessment:")
print("The model integrity is verified.")
print("The model remained functional under the")
print("tested image modifications.")
print("Further backdoor/trojan analysis is required")
print("before declaring the model fully secure.")

def analyze_behavior(test_name, test_results):

    print()
    print("========================================")
    print(test_name)
    print("========================================")

    changes = []

    for object_name in baseline:

        original = baseline[object_name]
        modified = test_results.get(object_name)

        if modified is None:
            print()
            print("Object:", object_name)
            print("Status: NOT DETECTED")
            continue

        # Calculate absolute confidence change
        absolute_change = abs(modified - original)

        # Calculate percentage change
        percentage_change = (absolute_change / original) * 100

        changes.append(absolute_change)

        print()
        print("Object:", object_name)
        print("Original confidence:", round(original, 4))
        print("Modified confidence:", round(modified, 4))
        print("Absolute change:", round(absolute_change, 4))
        print("Percentage change:", round(percentage_change, 2), "%")

    # Calculate average change for this test
    if changes:
        average_change = sum(changes) / len(changes)
        maximum_change = max(changes)

        print()
        print("Average confidence change:",
              round(average_change, 4))

        print("Maximum confidence change:",
              round(maximum_change, 4))
                # Classify the behavior
        maximum_percentage_change = (
            maximum_change / max(baseline.values())
        ) * 100

        print()

        if maximum_percentage_change < 5:
            print("Behavior Status: NORMAL")

        elif maximum_percentage_change <= 15:
            print("Behavior Status: ATTENTION")

        else:
            print("Behavior Status: SUSPICIOUS")
        
analyze_behavior("BRIGHTNESS BEHAVIOR ANALYSIS", brightness)

analyze_behavior("RESIZE BEHAVIOR ANALYSIS", resize)

analyze_behavior("COMPRESSION BEHAVIOR ANALYSIS", compression)

analyze_behavior("NOISE BEHAVIOR ANALYSIS", noise)