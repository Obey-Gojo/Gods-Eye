# Baseline confidence values
baseline = {
    "person": 0.8816,
    "motorcycle": 0.7597
}

# Brightness test confidence values
brightness_test = {
    "person": 0.8793,
    "motorcycle": 0.7721
}

print("================================")
print("     SECURITY COMPARISON")
print("================================")

for object_name in baseline:

    if object_name in brightness_test:

        original = baseline[object_name]
        modified = brightness_test[object_name]

        difference = modified - original

        print()
        print("Object:", object_name)
        print("Original confidence:", original)
        print("Modified confidence:", modified)
        print("Difference:", round(difference, 4))

print()
print("Conclusion:")
print("The model produced similar detections after")
print("the controlled brightness modification.")