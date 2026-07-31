import re
from typing import Dict, List, Optional

from modules.text_utils import normalize_text


SYMPTOMS = [
    "pain",
    "fever",
    "cough",
    "sore throat",
    "headache",
    "nausea",
    "vomiting",
    "diarrhea",
    "dizziness",
    "fatigue",
    "weakness",
    "shortness of breath",
    "breathing difficulty",
    "chest pain",
    "abdominal pain",
    "stomach pain",
    "belly pain",
    "rash",
    "itching",
    "swelling",
    "bleeding",
    "burning",
    "numbness",
    "tingling",
]

BODY_PARTS = [
    "head",
    "face",
    "eye",
    "ear",
    "nose",
    "throat",
    "neck",
    "chest",
    "abdomen",
    "stomach",
    "belly",
    "back",
    "arm",
    "hand",
    "leg",
    "foot",
    "knee",
    "hip",
    "shoulder",
    "wrist",
    "ankle",
]

CONDITIONS = [
    "diabetes",
    "diabetic",
    "hypertension",
    "high blood pressure",
    "asthma",
    "copd",
    "cancer",
    "pregnancy",
    "pregnant",
    "depression",
    "anxiety",
]

MED_TERMS = [
    "medicine",
    "medication",
    "antibiotic",
    "antibiotics",
    "pill",
    "tablet",
    "dose",
    "mg",
    "ml",
    "insulin",
    "ibuprofen",
    "paracetamol",
    "acetaminophen",
    "aspirin",
    "amoxicillin",
    "azithromycin",
    "metformin",
]

_DURATION_PATTERNS = [
    r"\bfor\s+\d+\s*(minute|minutes|hour|hours|day|days|week|weeks|month|months)\b",
    r"\bsince\s+(yesterday|today|last night|last week|last month)\b",
    r"\bfor\s+(one|two|three|four|five|six|seven|eight|nine|ten)\s*(day|days|week|weeks|month|months)\b",
    r"\bfor\s+a\s+couple\s+of\s+days\b",
    r"\b(started|began)\s+(yesterday|today|last night|last week|last month)\b",
    r"\b(started|began)\s+\d+\s*(day|days|week|weeks|month|months)\s+ago\b",
]


def _find_terms(normalized_text: str, terms: List[str]) -> List[str]:
    from modules.text_utils import is_negated
    matched: List[str] = []
    for term in terms:
        pattern = r"\b" + re.escape(term) + r"\b"
        for match in re.finditer(pattern, normalized_text):
            if is_negated(normalized_text, match.start(), match.end()):
                continue
            matched.append(term)
            break
    return matched


def extract_age(text: str) -> Optional[float]:
    normalized = normalize_text(text)
    # Match year-based age
    year_match = re.search(
        r"\b(\d{1,3})[\s-]*(year|years|yr|y/o|yo|year[\s-]*old|years[\s-]*old)\b",
        normalized,
    )
    if year_match:
        try:
            return float(year_match.group(1))
        except ValueError:
            pass

    # Match month-based age (e.g. "6 months old", "3mo")
    month_match = re.search(
        r"\b(\d{1,2})[\s-]*(month|months|mo|month[\s-]*old|months[\s-]*old)\b",
        normalized,
    )
    if month_match:
        try:
            months = float(month_match.group(1))
            return round(months / 12.0, 2)
        except ValueError:
            pass

    return None


def extract_durations(text: str) -> List[str]:
    normalized = normalize_text(text)
    matches: List[str] = []
    for pattern in _DURATION_PATTERNS:
        for match in re.finditer(pattern, normalized):
            matches.append(match.group(0))
    if "for" in normalized or "since" in normalized:
        for match in re.findall(r"\bfor\s+\d+\s*\w+\b", normalized):
            matches.append(match)
        for match in re.findall(r"\bsince\s+\w+\b", normalized):
            matches.append(match)
    return list(dict.fromkeys([m.strip() for m in matches if m]))


def parse_medical_query(text: str) -> Dict[str, object]:
    normalized = normalize_text(text)

    return {
        "normalized": normalized,
        "age": extract_age(text),
        "durations": extract_durations(text),
        "symptoms": _find_terms(normalized, SYMPTOMS),
        "body_parts": _find_terms(normalized, BODY_PARTS),
        "conditions": _find_terms(normalized, CONDITIONS),
        "med_terms": _find_terms(normalized, MED_TERMS),
    }
