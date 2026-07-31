import re
from typing import Dict, List

from modules.medical_extractor import extract_age
from modules.text_utils import normalize_text


_TOPIC_RULES = [
    {
        "topic": "pregnancy",
        "patterns": [
            r"\bpregnan(t|cy)\b",
            r"\btrimester\b",
            r"\bpostpartum\b",
        ],
    },
    {
        "topic": "pediatric",
        "patterns": [
            r"\bnewborn\b",
            r"\binfant\b",
            r"\btoddler\b",
            r"\bbaby\b",
            r"\bchild\b",
            r"\bkid\b",
        ],
    },
    {
        "topic": "elderly",
        "patterns": [
            r"\belderly\b",
            r"\bsenior\b",
        ],
    },
    {
        "topic": "anticoagulants",
        "patterns": [
            r"\bwarfarin\b",
            r"\banticoagulant\b",
            r"\bblood thinner\b",
        ],
    },
    {
        "topic": "insulin",
        "patterns": [
            r"\binsulin\b",
        ],
    },
    {
        "topic": "diabetes",
        "patterns": [
            r"\bdiabetes\b",
            r"\bdiabetic\b",
        ],
    },
    {
        "topic": "psychiatric_meds",
        "patterns": [
            r"\bantidepressant\b",
            r"\bantipsychotic\b",
            r"\bssri\b",
            r"\bbenzodiazepine\b",
            r"\bopioid\b",
        ],
    },
    {
        "topic": "immunocompromised",
        "patterns": [
            r"\btransplant\b",
            r"\bchemotherapy\b",
            r"\bimmunocompromised\b",
            r"\bhiv\b",
        ],
    },
]


def detect_high_impact_topics(query: str) -> Dict[str, object]:
    normalized = normalize_text(query)
    topics: List[str] = []

    for rule in _TOPIC_RULES:
        for pattern in rule["patterns"]:
            if re.search(pattern, normalized):
                topics.append(rule["topic"])
                break

    age = extract_age(normalized)
    if age is not None and (age < 5 or age >= 65):
        topics.append("age_high_risk")

    return {
        "flagged": bool(topics),
        "topics": topics,
        "age": age,
    }
