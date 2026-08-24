"""Turns whatever a user pastes (a bare username, an @handle, or a full TikTok URL)
into the plain username TikTokLiveClient expects."""

from __future__ import annotations

import re

# Matches tiktok.com/@username, with or without scheme/www, and an optional
# /live or /video/... or query string trailing after it.
_URL_RE = re.compile(r"tiktok\.com/@([\w.-]+)", re.IGNORECASE)


def extract_username(value: str) -> str:
    """Accepts a bare username, '@username', or a TikTok URL and returns the
    plain username (no '@', no URL)."""
    value = value.strip()
    match = _URL_RE.search(value)
    if match:
        return match.group(1)
    return value.lstrip("@")
