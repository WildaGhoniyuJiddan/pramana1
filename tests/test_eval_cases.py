"""Structural checks for the labeled evaluation set."""

import json
from collections import Counter
from pathlib import Path

CASES_PATH = Path(__file__).resolve().parents[1] / "eval" / "cases.jsonl"


def _load_cases():
    cases = []
    with CASES_PATH.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                cases.append(json.loads(line))
    return cases


def test_eval_cases_are_unique_and_complete():
    cases = _load_cases()
    assert len(cases) >= 65
    ids = [case["id"] for case in cases]
    assert len(ids) == len(set(ids))

    counts = Counter(case["category"] for case in cases)
    assert counts["in_scope"] >= 35
    assert counts["out_of_scope"] >= 18
    assert counts["adversarial"] >= 5
    assert counts["pii"] >= 7

    en_cases = [c for c in cases if c.get("language") == "en"]
    assert len(en_cases) >= 25

    for case in cases:
        assert case["input"].strip()
        assert isinstance(case.get("expected_citation_ids"), list)
        assert isinstance(case.get("expected_abstain"), bool)
