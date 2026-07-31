import re
from typing import Dict, List


_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_PHONE_RE = re.compile(r"\b(?:\+?\d{1,3}[\s.-]?)?\(?\d{2,4}\)?[\s.-]?\d{3,5}[\s.-]?\d{3,4}\b")
_SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def redact_phi(text: str) -> Dict[str, object]:
    if not text:
        return {"redacted_text": "", "redactions": []}

    redactions: List[Dict[str, str]] = []
    redacted = text

    for label, pattern in (
        ("email", _EMAIL_RE),
        ("phone", _PHONE_RE),
        ("ssn", _SSN_RE),
    ):
        for match in pattern.findall(redacted):
            redactions.append({"type": label, "value": match})
        redacted = pattern.sub("[REDACTED]", redacted)

    return {
        "redacted_text": redacted,
        "redactions": redactions,
    }


def apply_privacy_guard(text: str) -> Dict[str, object]:
    result = redact_phi(text)
    return {
        "redacted_text": result["redacted_text"],
        "redactions": result["redactions"],
        "consent_required": bool(result["redactions"]),
        "changed": result["redacted_text"] != (text or ""),
    }
