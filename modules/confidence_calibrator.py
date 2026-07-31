from typing import Dict, List


def calibrate_confidence(
    intent: Dict[str, object],
    risk: Dict[str, object],
    sufficiency: Dict[str, object],
    high_impact: Dict[str, object],
    coverage: Dict[str, object],
) -> Dict[str, object]:
    score = 0.9
    reasons: List[str] = []

    if coverage.get("non_medical"):
        score -= 0.3
        reasons.append("non_medical")

    if coverage.get("low_confidence"):
        score -= 0.25
        reasons.append("low_coverage_confidence")

    if sufficiency.get("status") == "INSUFFICIENT":
        score -= 0.2
        reasons.append("insufficient_info")

    if risk.get("level") == "MODERATE":
        score -= 0.1
        reasons.append("moderate_risk")

    if high_impact.get("flagged"):
        score -= 0.1
        reasons.append("high_impact")

    if intent.get("category") == "MEDICATION_GUIDANCE":
        score -= 0.05
        reasons.append("medication_request")

    score = max(0.0, min(1.0, score))
    low_confidence = score < 0.6

    if score < 0.4:
        label = "LOW"
    elif score < 0.7:
        label = "MEDIUM"
    else:
        label = "HIGH"

    force_escalation = low_confidence and (risk.get("level") == "MODERATE" or high_impact.get("flagged"))

    return {
        "score": round(score, 2),
        "label": label,
        "low_confidence": low_confidence,
        "reasons": reasons,
        "force_escalation": force_escalation,
    }
