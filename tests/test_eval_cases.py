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
    assert len(cases) == 45
    ids = [case["id"] for case in cases]
    assert len(ids) == len(set(ids))

    counts = Counter(case["category"] for case in cases)
    assert counts["in_scope"] == 15
    assert counts["triage"] == 10
    assert counts["out_of_scope"] == 10
    assert counts["adversarial"] == 4
    assert counts["pii"] == 6

    for case in cases:
        assert case["input"].strip()
        assert isinstance(case.get("expected_citation_ids"), list)
        assert isinstance(case.get("expected_abstain"), bool)
        if case["category"] in {"in_scope", "triage", "out_of_scope"}:
            assert case.get("expected_mode") in {
                "VERIFIED_GROUNDED",
                "NEEDS_CLARIFICATION",
                "OUT_OF_SCOPE_GUIDANCE",
            }


def test_critical_triage_case_has_rewrite_probe():
    cases = _load_cases()
    critical = next(case for case in cases if case["id"] == "triage-01")
    assert critical["input"] == (
        "direndahkan, disepelekan, dianggap tidak memiliki uang"
    )
    assert critical["expected_mode"] == "NEEDS_CLARIFICATION"
    assert critical["expected_guidance"] is True
    probe = critical["rewrite_probe"]
    assert probe["expected_mode"] == "VERIFIED_GROUNDED"
    assert set(probe["expected_citation_ids"]) & {
        "UU_08_1999_PASAL_4G",
        "UU_40_2008_PASAL_4",
    }
