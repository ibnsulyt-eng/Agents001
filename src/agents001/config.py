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
    model: str  # primary model — kept for display/back-compat, equals models[0]
    models: tuple[str, ...]  # full fallback chain, tried in order
    api_base: str
    max_revision_loops: int


# Free-tier model availability on aggregators like OpenRouter is volatile — models get
# pulled from the free pool with no warning (confirmed live: nvidia/nemotron-nano-9b-v2
# worked, then returned "No endpoints found" within the same session). A fallback chain
# tried in order is real resilience against that; a single hardcoded model isn't.
_PROVIDER_DEFAULTS = {
    "groq": {
        "api_base": "https://api.groq.com/openai/v1/chat/completions",
        "key_env": "GROQ_API_KEY",
        "model_env": "GROQ_MODEL",
        "default_models": ["llama-3.3-70b-versatile"],
    },
    "openrouter": {
        "api_base": "https://openrouter.ai/api/v1/chat/completions",
        "key_env": "OPENROUTER_API_KEY",
        "model_env": "OPENROUTER_MODEL",
        "default_models": [
            "nvidia/nemotron-3-super-120b-a12b:free",
            "google/gemma-4-31b-it:free",
            "z-ai/glm-5.2:free",
            "nvidia/nemotron-nano-9b-v2:free",
        ],
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

    model_env_raw = os.getenv(defaults["model_env"], "").strip()
    if model_env_raw:
        # Comma-separated list = explicit fallback chain; a single value still works.
        models = tuple(m.strip() for m in model_env_raw.split(",") if m.strip())
    else:
        models = tuple(defaults["default_models"])

    max_loops = int(os.getenv("MAX_REVISION_LOOPS", "2"))

    return Config(
        provider=provider,
        api_key=api_key,
        model=models[0],
        models=models,
        api_base=defaults["api_base"],
        max_revision_loops=max_loops,
    )
