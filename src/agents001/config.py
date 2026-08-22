"""Loads runtime configuration from environment variables (.env file)."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    provider: str
    api_key: str
    model: str
    api_base: str
    max_revision_loops: int


_PROVIDER_DEFAULTS = {
    "groq": {
        "api_base": "https://api.groq.com/openai/v1/chat/completions",
        "key_env": "GROQ_API_KEY",
        "model_env": "GROQ_MODEL",
        "default_model": "llama-3.3-70b-versatile",
    },
    "openrouter": {
        "api_base": "https://openrouter.ai/api/v1/chat/completions",
        "key_env": "OPENROUTER_API_KEY",
        "model_env": "OPENROUTER_MODEL",
        "default_model": "nvidia/nemotron-nano-9b-v2:free",
    },
}


def load_config() -> Config:
    provider = os.getenv("LLM_PROVIDER", "groq").strip().lower()
    if provider not in _PROVIDER_DEFAULTS:
        raise ValueError(
            f"Unknown LLM_PROVIDER '{provider}'. Supported: {', '.join(_PROVIDER_DEFAULTS)}"
        )

    defaults = _PROVIDER_DEFAULTS[provider]
    api_key = os.getenv(defaults["key_env"], "").strip()
    if not api_key:
        raise ValueError(
            f"Missing {defaults['key_env']}. Copy .env.example to .env and set your free "
            f"{provider} API key."
        )

    model = os.getenv(defaults["model_env"], defaults["default_model"]).strip()
    max_loops = int(os.getenv("MAX_REVISION_LOOPS", "2"))

    return Config(
        provider=provider,
        api_key=api_key,
        model=model,
        api_base=defaults["api_base"],
        max_revision_loops=max_loops,
    )
