import re
from typing import Dict, List

from modules.text_utils import normalize_text, is_negated


_HIGH_RISK_RULES = [
    {
        "category": "cardiac",
        "patterns": [
            r"\bchest pain\b",
            r"\bchest pressure\b",
            r"\bchest tightness\b",
            r"\bheart attack\b",
            r"\bcrushing chest\b",
        ],
    },
    {
        "category": "respiratory",
        "patterns": [
            r"\bshortness of breath\b",
            r"\bdifficulty breathing\b",
            r"\btrouble breathing\b",
            r"\bcannot breathe\b",
            r"\bhard to breathe\b",
            r"\bcan t breathe\b",
            r"\bnot breathing\b",
            r"\bblue lips\b",
        ],
    },
    {
        "category": "neurologic",
        "patterns": [
            r"\bstroke\b",
            r"\bseizure\b",
            r"\bunconscious\b",
            r"\bfainting\b",
            r"\bloss of consciousness\b",
            r"\bparalysis\b",
            r"\bslurred speech\b",
            r"\bvision loss\b",
            r"\bface droop\b",
            r"\bsudden weakness\b",
        ],
    },
    {
        "category": "bleeding",
        "patterns": [
            r"\bbleeding heavily\b",
            r"\bsevere bleeding\b",
            r"\buncontrolled bleeding\b",
            r"\bblood loss\b",
        ],
    },
    {
        "category": "severe_pain",
        "patterns": [
            r"\bsudden severe pain\b",
            r"\bworst headache\b",
        ],
    },
    {
        "category": "gi_emergency",
        "patterns": [
            r"\bsevere abdominal pain\b",
            r"\brigid abdomen\b",
            r"\bboardlike abdomen\b",
            r"\bvomiting blood\b",
            r"\bblood in vomit\b",
            r"\bcoffee ground vomit\b",
            r"\bblack stools\b",
            r"\bblack stool\b",
            r"\btarry stools\b",
            r"\brectal bleeding\b",
            r"\bblood in stool\b",
        ],
    },
]

_MODERATE_RISK_RULES = [
    {
        "category": "infection",
        "patterns": [
            r"\bfever\b",
            r"\bhigh fever\b",
            r"\binfection\b",
            r"\bchills\b",
        ],
    },
    {
        "category": "gi",
        "patterns": [
            r"\bvomiting\b",
            r"\bdiarrhea\b",
            r"\bnausea\b",
            r"\bdehydration\b",
        ],
    },
    {
        "category": "abdominal_pain",
        "patterns": [
            r"\babdominal pain\b",
            r"\babdomen pain\b",
            r"\bpain in (my|the) abdomen\b",
            r"\bstomach pain\b",
            r"\bpain in (my|the) stomach\b",
            r"\bbelly pain\b",
            r"\bupper abdominal pain\b",
            r"\blower abdominal pain\b",
        ],
    },
    {
        "category": "pain",
        "patterns": [
            r"\bpersistent pain\b",
            r"\bsevere pain\b",
            r"\bintense pain\b",
        ],
    },
    {
        "category": "swelling",
        "patterns": [
            r"\bswelling\b",
            r"\bedema\b",
        ],
    },
    {
        "category": "wound",
        "patterns": [
            r"\binfected wound\b",
            r"\bpus\b",
        ],
    },
]


def _match_rules(text: str, rules: List[Dict[str, object]]) -> List[Dict[str, str]]:
    matches: List[Dict[str, str]] = []
    for rule in rules:
        for pattern in rule["patterns"]:
            found = False
            for match in re.finditer(pattern, text):
                if is_negated(text, match.start(), match.end()):
                    continue
                matches.append({
                    "category": rule["category"],
                    "pattern": pattern,
                })
                found = True
                break
            if found:
                break
    return matches


def assess_risk(query: str) -> Dict[str, object]:
    normalized = normalize_text(query)
    word_count = len(normalized.split())

    high_matches = _match_rules(normalized, _HIGH_RISK_RULES)
    moderate_matches = _match_rules(normalized, _MODERATE_RISK_RULES)

    if high_matches:
        level = "HIGH"
    elif moderate_matches:
        level = "MODERATE"
    else:
        level = "SAFE"

    uncertain = word_count < 4 and level == "SAFE"

    return {
        "level": level,
        "high_matches": high_matches,
        "moderate_matches": moderate_matches,
        "uncertain": uncertain,
        "word_count": word_count,
    }


def check_risk(query: str) -> str:
    return assess_risk(query)["level"]
