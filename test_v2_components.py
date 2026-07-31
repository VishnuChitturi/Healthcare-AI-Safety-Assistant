from modules.confidence_calibrator import calibrate_confidence
from modules.escalation_router import decide_escalation
from modules.privacy_guard import apply_privacy_guard
from modules.retrieval_layer import retrieve_evidence


def assert_equal(actual, expected, label):
    if actual != expected:
        raise AssertionError(f"{label} | expected={expected} actual={actual}")


privacy = apply_privacy_guard("Email me at test@example.com")
assert_equal(privacy["consent_required"], True, "privacy_redaction")

retrieval = retrieve_evidence("sore throat for 2 days")
assert_equal(retrieval["used"], True, "retrieval_used")

confidence = calibrate_confidence(
    {"category": "MEDICAL_ADVICE"},
    {"level": "SAFE"},
    {"status": "SUFFICIENT"},
    {"flagged": False},
    {"low_confidence": False, "non_medical": False},
)
assert_equal(confidence["label"], "HIGH", "confidence_label")

escalation = decide_escalation("EMERGENCY_ADVICE", confidence)
assert_equal(escalation["escalate"], True, "escalation_emergency")

print("v2 component tests passed.")