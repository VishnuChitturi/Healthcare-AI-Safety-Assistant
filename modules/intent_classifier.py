import re
from typing import Dict, List

from modules.text_utils import normalize_text


_INTENT_RULES = [
    {
        "category": "SELF_HARM",
        "patterns": [
            r"\bkill myself\b",
            r"\bkill me\b",
            r"\bend my life\b",
            r"\bsuicide\b",
            r"\bself harm\b",
            r"\bself-harm\b",
            r"\bcut myself\b",
            r"\bwant to die\b",
            r"\bdont want to live\b",
            r"\bdon t want to live\b",
        ],
        "confidence": 0.95,
    },
    {
        "category": "OVERDOSE_MISUSE",
        "patterns": [
            r"\boverdose\b",
            r"\blethal dose\b",
            r"\bfatal dose\b",
            r"\bhow many (pills|tablets|mg|ml)\b",
            r"\bwhat (dose|amount) (kills|is lethal|is fatal)\b",
            r"\bmaximum (dose|amount)\b",
            r"\bhow to take (too many|a lot)\b",
            r"\bcan (taking|mixing) .* kill\b",
        ],
        "confidence": 0.9,
    },
    {
        "category": "VIOLENCE",
        "patterns": [
            r"\bkill (him|her|them|someone)\b",
            r"\bhurt (him|her|them|someone)\b",
            r"\bpoison (him|her|them|someone)\b",
            r"\bmake someone sick\b",
        ],
        "confidence": 0.85,
    },
    {
        "category": "ILLEGAL_MISUSE",
        "patterns": [
            r"\bwithout prescription\b",
            r"\bbuy .* without\b",
            r"\bmake .* drug\b",
            r"\bsteal .* medication\b",
        ],
        "confidence": 0.8,
    },
    {
        "category": "MEDICATION_GUIDANCE",
        "patterns": [
            r"\bantibiotic(s)?\b",
            r"\bshould i take (medicine|medication|antibiotic(s)?|pill|tablet|drug|ibuprofen|paracetamol|acetaminophen|aspirin|amoxicillin|azithromycin|metformin|insulin)\b",
            r"\bcan i take (medicine|medication|antibiotic(s)?|pill|tablet|drug|ibuprofen|paracetamol|acetaminophen|aspirin|amoxicillin|azithromycin|metformin|insulin)\b",
            r"\bshould i use (medicine|medication|antibiotic(s)?|cream|ointment)\b",
            r"\bdo i need (medicine|medication|antibiotic(s)?)\b",
            r"\bwhat (medicine|medication|antibiotic(s)?)\b",
            r"\bwhich (medicine|medication|antibiotic(s)?)\b",
            r"\bmedication for\b",
            r"\bdose of (ibuprofen|paracetamol|acetaminophen|aspirin|amoxicillin|azithromycin|metformin|insulin)\b",
        ],
        "confidence": 0.75,
    },
    {
        "category": "GREETING_OR_CLOSURE",
        "patterns": [
            r"\b(hello|hi|hey|greetings|howdy)\b",
            r"\b(thanks|thank\s+you|thankyou|grateful|appreciate\s+it)\b",
            r"\b(bye|goodbye|see\s+you|farewell)\b",
            r"\b(ok|okay|fine|understood)\b",
        ],
        "confidence": 0.8,
    },
]


def _match_patterns(text: str, patterns: List[str]) -> List[str]:
    matches = []
    for pattern in patterns:
        if re.search(pattern, text):
            matches.append(pattern)
    return matches


def classify_intent(query: str) -> Dict[str, object]:
    normalized = normalize_text(query)

    for rule in _INTENT_RULES:
        matched = _match_patterns(normalized, rule["patterns"])
        if matched:
            category = rule["category"]
            if category == "GREETING_OR_CLOSURE":
                # Bypass greeting check if query contains any medical indicators
                from modules.medical_extractor import parse_medical_query
                parsed = parse_medical_query(query)
                if parsed["symptoms"] or parsed["conditions"] or parsed["med_terms"]:
                    continue
            return {
                "category": category,
                "matched": matched,
                "confidence": rule["confidence"],
            }

    return {
        "category": "MEDICAL_ADVICE",
        "matched": [],
        "confidence": 0.6,
    }
