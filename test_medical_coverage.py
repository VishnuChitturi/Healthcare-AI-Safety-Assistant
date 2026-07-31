from modules.medical_coverage import classify_medical_coverage


def assert_equal(actual, expected, label):
    if actual != expected:
        raise AssertionError(f"{label} | expected={expected} actual={actual}")


medical = classify_medical_coverage("I have chest pain and shortness of breath")
assert_equal(medical["is_medical"], True, "medical_yes")

non_medical = classify_medical_coverage("hello how are you")
assert_equal(non_medical["non_medical"], True, "medical_no")

low = classify_medical_coverage("help")
assert_equal(low["low_confidence"], True, "medical_low_confidence")

print("Medical coverage tests passed.")
