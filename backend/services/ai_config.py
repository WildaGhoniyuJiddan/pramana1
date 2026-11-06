"""AI runtime configuration for Pramana.

AI_MODE controls whether AI is mandatory, optional for local development, or
disabled for retrieval-only evaluation:

- required: no silent template fallback for user-facing AI output.
- optional: deterministic fallback is allowed (development/tests).
- disabled: AI calls are skipped entirely.
"""

import os
from typing import List

from dotenv import load_dotenv

load_dotenv()

VALID_AI_MODES = {"required", "optional", "disabled"}
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash").strip()
GEMINI_EMBEDDING_MODEL = os.getenv(
    "GEMINI_EMBEDDING_MODEL", "gemini-embedding-001"
).strip()
DEFAULT_GEMINI_FALLBACKS = (
    "gemini-3.1-flash-lite,gemini-3.5-flash-lite,gemini-3.6-flash"
)


def get_gemini_model_chain() -> List[str]:
    """Return the primary model followed by configured fallback models.

    ``GEMINI_MODEL`` remains the primary model for backward compatibility.
    ``GEMINI_MODEL_FALLBACKS`` is a comma-separated ordered chain. Duplicates
    are removed while preserving order.
    """
    primary = os.getenv("GEMINI_MODEL", GEMINI_MODEL).strip() or GEMINI_MODEL
    fallback_text = os.getenv(
        "GEMINI_MODEL_FALLBACKS", DEFAULT_GEMINI_FALLBACKS
    )
    chain: List[str] = []
    for model in [primary] + [
        item.strip() for item in fallback_text.split(",")
    ]:
        if model and model not in chain:
            chain.append(model)
    return chain


def get_ai_mode() -> str:
    value = os.getenv("AI_MODE", "required").strip().lower()
    return value if value in VALID_AI_MODES else "required"


def get_gemini_api_key() -> str:
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key or key == "your_gemini_api_key_here":
        return ""
    return key


def ai_enabled() -> bool:
    return get_ai_mode() != "disabled" and bool(get_gemini_api_key())
