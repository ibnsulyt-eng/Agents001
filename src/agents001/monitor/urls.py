"""Turns whatever a user pastes (a bare username, an @handle, a full TikTok URL, or a
shortened vt.tiktok.com link) into the plain username TikTokLiveClient expects."""

from __future__ import annotations

import re

import requests

# Matches tiktok.com/@username, with or without scheme/www, and an optional
# /live or /video/... or query string trailing after it.
_URL_RE = re.compile(r"tiktok\.com/@([\w.-]+)", re.IGNORECASE)

# Shortened share links (vt.tiktok.com/... or www.tiktok.com/t/...) redirect to the
# real @username URL but don't contain it themselves — needs an HTTP round-trip.
_SHORT_LINK_RE = re.compile(r"(vt\.tiktok\.com|tiktok\.com/t)/", re.IGNORECASE)


def extract_username(value: str) -> str:
    """Accepts a bare username, '@username', a TikTok URL, or a vt.tiktok.com
    short link and returns the plain username (no '@', no URL)."""
    value = value.strip()

    match = _URL_RE.search(value)
    if match:
        return match.group(1)

    if _SHORT_LINK_RE.search(value):
        resolved = _resolve_redirect(value)
        match = _URL_RE.search(resolved)
        if match:
            return match.group(1)
        raise ValueError(f"Could not find a username after resolving short link: {value}")

    return value.lstrip("@")


def _resolve_redirect(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    resp = requests.head(url, allow_redirects=True, timeout=10)
    return resp.url
