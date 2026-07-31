import json
import os
from datetime import datetime
import threading

from modules.confidence_calibrator import calibrate_confidence


_LOG_LOCK = threading.Lock()
from modules.escalation_router import decide_escalation
from modules.high_impact import detect_high_impact_topics
from modules.intent_classifier import classify_intent
from modules.medical_coverage import classify_medical_coverage
from modules.privacy_guard import apply_privacy_guard
from modules.retrieval_layer import retrieve_evidence
from modules.risk_classifier import assess_risk
from modules.safety_rules import decide_action
from modules.sufficiency_checker import check_sufficiency, heuristic_sufficiency
from modules.text_utils import build_context


def process_query(query_or_history, llm_enabled: bool = True, max_turns: int = 3):
    # Validate input length to prevent Denial of Service (DoS) and ReDoS
    if isinstance(query_or_history, list):
        for turn in query_or_history:
            if not isinstance(turn, str) or len(turn) > 1000:
                raise ValueError("Individual chat messages must be strings under 1000 characters.")
    elif isinstance(query_or_history, str):
        if len(query_or_history) > 1000:
            raise ValueError("Query string must be under 1000 characters.")
    else:
        raise ValueError("Query must be a string or a list of strings.")

    context = build_context(query_or_history, max_turns=max_turns)

    # Step 0 - Privacy guard
    privacy_current = apply_privacy_guard(context["current"])
    privacy_recent = apply_privacy_guard(context["recent_text"])

    redacted_current = privacy_current["redacted_text"]
    redacted_recent = privacy_recent["redacted_text"]

    # Step 1 - Rule-based intent and risk
    intent = classify_intent(redacted_current)
    risk = assess_risk(redacted_recent)
    high_impact = detect_high_impact_topics(redacted_recent)

    coverage_current = classify_medical_coverage(redacted_current)
    coverage_recent = classify_medical_coverage(redacted_recent)
    is_medical = coverage_current["is_medical"] or coverage_recent["is_medical"]
    if intent["category"] == "MEDICATION_GUIDANCE":
        is_medical = True
    coverage = {
        "is_medical": is_medical,
        "non_medical": coverage_current["non_medical"] and coverage_recent["non_medical"],
        "confidence": max(coverage_current["confidence"], coverage_recent["confidence"]),
        "low_confidence": coverage_current["low_confidence"] or coverage_recent["low_confidence"],
        "details": {
            "current": coverage_current,
            "recent": coverage_recent,
        },
    }

    # Step 2 - Sufficiency (only after rule-first gating)
    if intent["category"] in ("SELF_HARM", "OVERDOSE_MISUSE", "VIOLENCE", "ILLEGAL_MISUSE"):
        sufficiency = {
            "status": "SKIPPED",
            "source": "rule",
            "raw": "",
            "errors": [],
        }
    elif risk["level"] == "HIGH":
        sufficiency = {
            "status": "SKIPPED",
            "source": "rule",
            "raw": "",
            "errors": [],
        }
    elif coverage["non_medical"] or coverage["low_confidence"]:
        sufficiency = {
            "status": "SKIPPED",
            "source": "rule",
            "raw": "",
            "errors": [],
        }
    else:
        sufficiency = check_sufficiency(redacted_recent) if llm_enabled else heuristic_sufficiency(redacted_recent)

    # Step 2.5 - Retrieval / knowledge grounding (stub)
    retrieval = retrieve_evidence(redacted_recent, max_results=3) if coverage["is_medical"] else {"evidence": [], "used": False}

    # Step 3 - Confidence calibration
    confidence_info = calibrate_confidence(intent, risk, sufficiency, high_impact, coverage)

    # Step 4 - Decision rules
    consent_required = privacy_current["consent_required"] or privacy_recent["consent_required"]
    decision_core = decide_action(
        intent,
        risk,
        sufficiency,
        high_impact,
        coverage,
        confidence_info,
        consent_required=consent_required
    )

    # Step 5 - Escalation routing
    escalation = decide_escalation(decision_core["action"], confidence_info)

    decision = {
        "redacted_query": redacted_current,
        "risk": risk["level"],
        "risk_detail": risk,
        "intent": intent["category"],
        "intent_detail": intent,
        "sufficiency": sufficiency.get("status", "INSUFFICIENT"),
        "sufficiency_detail": sufficiency,
        "missing_fields": sufficiency.get("missing_fields", []),
        "high_impact": high_impact,
        "coverage": coverage,
        "action": decision_core["action"],
        "confidence": decision_core["confidence"],
        "reasons": decision_core["reasons"],
        "confidence_calibration": confidence_info,
        "retrieval": retrieval,
        "escalation": escalation,
        "llm_enabled": llm_enabled,
    }

    # Step 4 - Structured logging for auditing
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "current_query": redacted_current,
        "recent_context": redacted_recent,
        "privacy": {
            "current": privacy_current["redactions"],
            "recent": privacy_recent["redactions"],
        },
        "decision": decision,
    }

    with _LOG_LOCK:
        with open("logs/system_log.txt", "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    return decision