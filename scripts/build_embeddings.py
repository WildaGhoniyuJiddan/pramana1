"""Build pre-computed corpus embeddings for optional hybrid retrieval.

Run from the repository root with a real Gemini API key:

    python scripts/build_embeddings.py

The output is ``corpus/embeddings.json``. It contains only public corpus text
vectors, model metadata, and a corpus checksum. Do not commit secrets.
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.services.ai_config import GEMINI_EMBEDDING_MODEL, get_gemini_api_key
from backend.services.corpus_loader import CorpusManager
from backend.services.hybrid_retrieval import (
    EMBEDDINGS_PATH,
    corpus_checksum,
    embed_text,
)


def main() -> int:
    if not get_gemini_api_key():
        print("GEMINI_API_KEY is required.", file=sys.stderr)
        return 1

    corpus = CorpusManager.get_instance()
    vectors = {}
    for index, reg in enumerate(corpus.get_all(), start=1):
        text = reg.get("text", "")
        if not text:
            continue
        vectors[reg["id"]] = embed_text(
            text, task_type="RETRIEVAL_DOCUMENT"
        )
        print(f"[{index}/{len(corpus.get_all())}] {reg['id']}")
        time.sleep(0.2)

    dimension = len(next(iter(vectors.values()))) if vectors else 0
    payload = {
        "model": GEMINI_EMBEDDING_MODEL,
        "dimension": dimension,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "corpus_checksum": corpus_checksum(corpus),
        "vectors": vectors,
    }
    path = Path(EMBEDDINGS_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(vectors)} vectors to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
