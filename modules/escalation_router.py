from typing import Dict


def decide_escalation(action: str, confidence: Dict[str, object]) -> Dict[str, object]:
    if action in ("SELF_HARM_CRISIS", "EMERGENCY_ADVICE"):
        return {
            "escalate": True,
            "reason": "critical_action",
            "level": "immediate",
        }

    if confidence.get("force_escalation"):
        return {
            "escalate": True,
            "reason": "low_confidence",
            "level": "review",
        }

    return {
        "escalate": False,
        "reason": "none",
        "level": "none",
    }


def route_escalation(action: str, confidence: Dict[str, object]) -> Dict[str, object]:
    return decide_escalation(action, confidence)
