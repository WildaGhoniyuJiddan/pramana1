"""AI runtime configuration for Pramana.

AI_MODE controls whether AI is mandatory, optional for local development, or
disabled for retrieval-only evaluation:

- required: no silent template fallback for user-facing AI output.
- optional: deterministic fallback is allowed (development/tests).
- disabled: AI calls are skipped entirely.
"""

import os

VALID_AI_MODES = {"required", "optional", "disabled"}
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
GEMINI_EMBEDDING_MODEL = os.getenv(
    "GEMINI_EMBEDDING_MODEL", "gemini-embedding-001"
)


def get_ai_mode() -> str:
    value = os.getenv("AI_MODE", "optional").strip().lower()
    return value if value in VALID_AI_MODES else "optional"


def get_gemini_api_key() -> str:
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key or key == "your_gemini_api_key_here":
        return ""
    return key


def ai_enabled() -> bool:
    return get_ai_mode() != "disabled" and bool(get_gemini_api_key())
