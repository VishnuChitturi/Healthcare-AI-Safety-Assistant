from typing import Dict, List


def decide_action(
    intent: Dict[str, object],
    risk: Dict[str, object],
    sufficiency: Dict[str, object],
    high_impact: Dict[str, object],
    coverage: Dict[str, object],
    confidence: Dict[str, object],
    consent_required: bool = False,
) -> Dict[str, object]:
    reasons: List[str] = []

    if consent_required:
        reasons.append("consent_required")
        return {
            "action": "PRIVACY_REFUSAL",
            "confidence": 0.95,
            "reasons": reasons,
        }

    intent_category = intent.get("category", "MEDICAL_ADVICE")

    if intent_category == "GREETING_OR_CLOSURE":
        reasons.append("greeting_or_closure")
        return {
            "action": "GREETING_OR_CLOSURE",
            "confidence": 0.9,
            "reasons": reasons,
        }

    risk_level = risk.get("level", "SAFE")
    sufficiency_status = sufficiency.get("status", "INSUFFICIENT")

    if intent_category in ("SELF_HARM", "OVERDOSE_MISUSE"):
        reasons.append("intent_self_harm_or_overdose")
        return {
            "action": "SELF_HARM_CRISIS",
            "confidence": 0.95,
            "reasons": reasons,
        }

    if intent_category in ("VIOLENCE", "ILLEGAL_MISUSE"):
        reasons.append("intent_unsafe_request")
        return {
            "action": "SAFETY_REFUSAL",
            "confidence": 0.9,
            "reasons": reasons,
        }

    if risk_level == "HIGH":
        reasons.append("risk_high")
        return {
            "action": "EMERGENCY_ADVICE",
            "confidence": 0.95,
            "reasons": reasons,
        }

    if coverage.get("non_medical"):
        reasons.append("non_medical")
        return {
            "action": "ASK_CLARIFY",
            "confidence": 0.7,
            "reasons": reasons,
        }

    if sufficiency_status == "INSUFFICIENT" or risk.get("uncertain"):
        if intent_category == "MEDICATION_GUIDANCE":
            reasons.append("medication_request")
        else:
            reasons.append("insufficient_info")
        return {
            "action": "ASK_MORE_INFO",
            "confidence": 0.8,
            "reasons": reasons,
        }

    if confidence.get("force_escalation"):
        reasons.append("low_confidence_escalation")
        return {
            "action": "HUMAN_ESCALATION",
            "confidence": 0.8,
            "reasons": reasons,
        }

    if intent_category == "MEDICATION_GUIDANCE":
        reasons.append("medication_request")
        return {
            "action": "CAUTION_ADVICE",
            "confidence": 0.85,
            "reasons": reasons,
        }

    if coverage.get("low_confidence"):
        reasons.append("low_confidence")
        return {
            "action": "ASK_MORE_INFO",
            "confidence": 0.75,
            "reasons": reasons,
        }

    if high_impact.get("flagged") or risk_level == "MODERATE":
        reasons.append("caution_required")
        return {
            "action": "CAUTION_ADVICE",
            "confidence": 0.85,
            "reasons": reasons,
        }

    reasons.append("low_risk")
    return {
        "action": "SAFE_TO_RESPOND",
        "confidence": 0.85,
        "reasons": reasons,
    }
