import json
import re
from pathlib import Path

def test_i18n_dictionary_parity():
    """Verify that both ID and EN have identical key sets in i18n.svelte.js."""
    i18n_file = Path("frontend/src/lib/i18n.svelte.js")
    assert i18n_file.exists()
    content = i18n_file.read_text(encoding="utf-8")

    # Extract ID keys
    id_match = re.search(r"id:\s*\{([^}]+(?:\{[^}]+\}[^}]+)*)\}", content)
    en_match = re.search(r"en:\s*\{([^}]+(?:\{[^}]+\}[^}]+)*)\}", content)
    assert id_match and en_match

    def extract_keys(block):
        # find top-level keys like `keyName:`
        return set(re.findall(r"^\s*([a-zA-Z0-9_]+):", block, re.MULTILINE))

    id_keys = extract_keys(id_match.group(1))
    en_keys = extract_keys(en_match.group(1))

    diff_id_en = id_keys - en_keys
    diff_en_id = en_keys - id_keys

    assert not diff_id_en, f"Keys in ID but missing in EN: {diff_id_en}"
    assert not diff_en_id, f"Keys in EN but missing in ID: {diff_en_id}"
