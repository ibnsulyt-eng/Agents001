"""Fast, free, offline first-pass filters — catch the obvious stuff before it ever
reaches the LLM, so the paid/rate-limited path only sees ambiguous cases."""

from __future__ import annotations

import re


def check_keywords(text: str, banned_keywords: list[str]) -> str | None:
    """Return the matched keyword if text contains a banned term, else None."""
    lowered = text.lower()
    for kw in banned_keywords:
        if kw and kw in lowered:
            return kw
    return None


_URL_RE = re.compile(r"https?://|www\.", re.IGNORECASE)
_REPEATED_CHAR_RE = re.compile(r"(.)\1{6,}")  # e.g. "aaaaaaaa"


def looks_like_spam(text: str) -> str | None:
    """Cheap heuristics for spam/bot-like text, independent of the LLM."""
    if _URL_RE.search(text):
        return "contains a link"
    if _REPEATED_CHAR_RE.search(text):
        return "excessive character repetition"
    stripped = text.replace(" ", "")
    if len(stripped) > 10 and len(set(stripped)) <= 2:
        return "low-entropy repeated text"
    return None
