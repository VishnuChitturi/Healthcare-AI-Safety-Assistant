import re
from typing import Any, Dict, List


def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"[^\w\s\-/]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_context(query_or_history: Any, max_turns: int = 3) -> Dict[str, Any]:
    if isinstance(query_or_history, list):
        turns = [str(t) for t in query_or_history if t is not None]
    else:
        turns = [str(query_or_history)]

    turns = [t.strip() for t in turns if t.strip()]
    current = turns[-1] if turns else ""

    if max_turns and max_turns > 0:
        recent_turns = turns[-max_turns:]
    else:
        recent_turns = turns

    recent_text = " ".join(recent_turns)

    return {
        "current": current,
        "recent_turns": recent_turns,
        "recent_text": recent_text,
        "all_turns": turns,
    }


def is_negated(text: str, match_start: int, match_end: int) -> bool:
    # Pre-match negation check
    pre_window = text[max(0, match_start - 60):match_start]
    pre_negated = bool(
        re.search(
            r"\b(no|not|dont|don|without|denies|deny|denied)\b(?:\s+(?!but|however|except|yet|although|though)\b[\w-]+\b){0,7}\s*$",
            pre_window,
        )
    )
    if pre_negated:
        return True

    # Post-match negation check (e.g. "chest pain is absent", "chest pain: none")
    post_window = text[match_end:min(len(text), match_end + 30)]
    post_negated = bool(
        re.search(
            r"^\s*(?:is\s+)?(?:absent|none|negative|denies|deny|denied)\b",
            post_window,
        )
    )
    return post_negated
