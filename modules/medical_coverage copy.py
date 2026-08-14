import re
from typing import Dict, List

from modules.medical_extractor import parse_medical_query
from modules.text_utils import normalize_text


_NON_MEDICAL_PATTERNS = [
    r"\bhello\b",
    r"\bhi\b",
    r"\bhey\b",
    r"\bhow are you\b",
    r"\bthank you\b",
    r"\bthanks\b",
    r"\bjoke\b",
    r"\bmovie\b",
    r"\bmusic\b",
    r"\bsport\b",
    r"\bfootball\b",
    r"\bcricket\b",
    r"\bweather\b",
    r"\bpython\b",
    r"\bjava\b",
    r"\bjavascript\b",
    r"\bcoding\b",
    r"\bprogramming\b",
    r"\blaptop\b",
    r"\bphone\b",
    r"\binternet\b",
    r"\bmath\b",
    r"\bschool\b",
    r"\bhomework\b",
]


def _matches_non_medical(normalized_text: str) -> List[str]:
    matches = []
    for pattern in _NON_MEDICAL_PATTERNS:
        if re.search(pattern, normalized_text):
            matches.append(pattern)
    return matches


def classify_medical_coverage(text: str) -> Dict[str, object]:
    normalized = normalize_text(text)
    parsed = parse_medical_query(text)

    symptom_count = len(parsed["symptoms"])
    body_count = len(parsed["body_parts"])
    condition_count = len(parsed["conditions"])
    med_count = len(parsed["med_terms"])

    confidence = 0.0
    if symptom_count:
        confidence += 0.5
    if condition_count:
        confidence += 0.4
    if med_count:
        confidence += 0.4
    if body_count:
        confidence += 0.2

    confidence = min(confidence, 1.0)
    is_medical = confidence > 0.0

    non_medical_matches = []
    if not is_medical:
        non_medical_matches = _matches_non_medical(normalized)

    non_medical = bool(non_medical_matches) and not is_medical
    low_confidence = (confidence < 0.35) and not non_medical

    return {
        "is_medical": is_medical,
        "confidence": confidence,
        "low_confidence": low_confidence,
        "non_medical": non_medical,
        "non_medical_matches": non_medical_matches,
        "signals": parsed,
    }
