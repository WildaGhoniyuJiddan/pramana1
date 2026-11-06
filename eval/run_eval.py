"""Pramana evaluation harness with epistemic-routing metrics.

Runs a labeled set of in-scope, triage, out-of-scope, adversarial, and PII
cases. The default run uses whatever AI mode is configured. Use
``--retrieval-only`` or ``--mode fast`` for a deterministic baseline, and
``--mode live`` for a rate-limit-safe live Gemini evaluation.

Usage:
    python eval/run_eval.py
    python eval/run_eval.py --mode fast
    python eval/run_eval.py --mode live
"""

import argparse
import json
import os
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CASES_PATH = ROOT / "eval" / "cases.jsonl"
RESULTS_DIR = ROOT / "eval" / "results"
NON_GROUNDED_MODES = {"NEEDS_CLARIFICATION", "OUT_OF_SCOPE_GUIDANCE"}


def load_cases():
    cases = []
    with CASES_PATH.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                cases.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line {line_number}: {exc}"
                ) from exc
    return cases


def validate_citations(engine, result):
    """Independently check every emitted citation and claim span."""
    from backend.services.evidence_spans import build_span_index

    citations = result.get("citations") or []
    claims = result.get("ai_claims") or []
    citation_by_id = {}
    citations_valid = 0
    for citation in citations:
        reg_id = citation.get("reg_id")
        quote = citation.get("quoted_text") or ""
        reg = engine.corpus_mgr.get_by_id(reg_id)
        if not reg:
            continue
        normalized_quote = " ".join(quote.split())
        normalized_text = " ".join(reg.get("text", "").split())
        if normalized_quote and normalized_quote in normalized_text:
            citations_valid += 1
            citation_by_id[reg_id] = citation

    span_index = build_span_index(citations)
    claims_valid = 0
    for claim in claims:
        citation_id = claim.get("citation_id")
        span_ids = claim.get("span_ids") or []
        if citation_id not in citation_by_id or not span_ids:
            continue
        if all(
            span_id in span_index
            and span_index[span_id]["citation_id"] == citation_id
            for span_id in span_ids
        ):
            claims_valid += 1

    return {
        "citations_emitted": len(citations),
        "citations_valid": citations_valid,
        "claims_emitted": len(claims),
        "claims_valid": claims_valid,
    }


def guidance_is_complete(result):
    guidance = result.get("user_guidance") or {}
    return bool(
        guidance.get("missing_context_diagnosis")
        and guidance.get("what_user_should_do_next")
        and len(guidance.get("suggested_query_rewrites") or []) >= 3
        and guidance.get("relevant_authority_or_channel")
    )


def run_case(engine, case, ai_active=False):
    started = time.perf_counter()
    result = engine.analyze_viral_post(case["input"])
    latency_ms = int((time.perf_counter() - started) * 1000)

    citations = result.get("citations", [])
    citation_ids = [citation.get("reg_id") for citation in citations]
    expected = case.get("expected_citation_ids", [])
    category = case.get("category", "in_scope")
    expected_mode = case.get("expected_mode")
    actual_mode = result.get("resolution_mode", "UNKNOWN")
    guidance_complete = guidance_is_complete(result)
    validation = validate_citations(engine, result)

    forbidden_hits = []
    if case.get("forbidden_terms"):
        text_parts = [
            result.get("neutral_summary") or "",
            result.get("neutral_summary_en") or "",
            result.get("copyable_comment") or "",
            result.get("detected_framing_or_tone") or "",
        ]
        guidance = result.get("user_guidance") or {}
        for key in (
            "missing_context_diagnosis",
            "what_user_should_do_next",
            "suggested_query_rewrites",
        ):
            text_parts.extend(guidance.get(key) or [])
        text_parts.append(guidance.get("relevant_authority_or_channel") or "")
        text_parts.extend(
            claim.get("claim_text", "")
            for claim in result.get("ai_claims", [])
        )
        haystack = " ".join(text_parts).lower()
        forbidden_hits = [
            term for term in case["forbidden_terms"]
            if term.lower() in haystack
        ]

    leaked_pii = []
    if case.get("pii_tokens"):
        masked = result.get("masked_post") or ""
        leaked_pii = [
            token for token in case["pii_tokens"]
            if token.lower() in masked.lower()
        ]

    probe_result = None
    probe_passed = True
    if case.get("rewrite_probe"):
        probe = case["rewrite_probe"]
        probe_started = time.perf_counter()
        probe_result_raw = engine.analyze_viral_post(probe["input"])
        probe_latency = int((time.perf_counter() - probe_started) * 1000)
        probe_citations = [
            citation.get("reg_id")
            for citation in probe_result_raw.get("citations", [])
        ]
        probe_passed = (
            probe_result_raw.get("resolution_mode") == probe.get("expected_mode")
            and any(
                item in probe_citations
                for item in probe.get("expected_citation_ids", [])
            )
        )
        probe_result = {
            "input": probe["input"],
            "resolution_mode": probe_result_raw.get("resolution_mode"),
            "citation_ids": probe_citations,
            "passed": probe_passed,
            "latency_ms": probe_latency,
        }

    if category == "pii":
        passed = not leaked_pii
    elif category == "out_of_scope":
        passed = (
            actual_mode == expected_mode
            and result.get("status") == "TIDAK_DITEMUKAN"
            and not citations
            and guidance_complete
        )
    elif category == "triage":
        passed = (
            actual_mode == expected_mode
            and not citations
            and not result.get("ai_claims")
            and guidance_complete
        )
    elif category == "adversarial":
        passed = (
            not forbidden_hits
            and not citations
            and not result.get("ai_claims")
            and actual_mode in NON_GROUNDED_MODES
        )
    else:
        passed = actual_mode == expected_mode
        if expected:
            passed = passed and any(item in citation_ids for item in expected)

    if case.get("rewrite_probe"):
        passed = passed and probe_passed

    return {
        "id": case["id"],
        "category": category,
        "passed": bool(passed),
        "status": result.get("status"),
        "resolution_mode": actual_mode,
        "expected_mode": expected_mode,
        "epistemic_tier": result.get("epistemic_tier"),
        "guidance_complete": guidance_complete,
        "ai_synthesis_status": result.get("ai_synthesis_status"),
        "citation_ids": citation_ids,
        "expected_citation_ids": expected,
        "forbidden_hits": forbidden_hits,
        "leaked_pii": leaked_pii,
        "latency_ms": latency_ms,
        "citations_emitted": validation["citations_emitted"],
        "citations_valid": validation["citations_valid"],
        "claims_emitted": validation["claims_emitted"],
        "claims_valid": validation["claims_valid"],
        "rewrite_probe": probe_result,
    }


def summarize(cases, results):
    total = len(results)
    passed = sum(1 for result in results if result["passed"])
    in_scope = [r for r in results if r["category"] == "in_scope"]
    triage = [r for r in results if r["category"] == "triage"]
    out_scope = [r for r in results if r["category"] == "out_of_scope"]
    adversarial = [r for r in results if r["category"] == "adversarial"]
    pii = [r for r in results if r["category"] == "pii"]
    non_grounded = triage + out_scope
    labeled = [r for r in results if r.get("expected_mode")]

    citations_emitted = sum(r["citations_emitted"] for r in results)
    citations_valid = sum(r["citations_valid"] for r in results)
    claims_emitted = sum(r["claims_emitted"] for r in results)
    claims_valid = sum(r["claims_valid"] for r in results)
    probes = [
        r["rewrite_probe"] for r in results
        if r.get("rewrite_probe")
    ]

    latencies = sorted(result["latency_ms"] for result in results)
    p95 = (
        latencies[
            min(len(latencies) - 1, int(round(0.95 * (len(latencies) - 1))))
        ]
        if latencies else 0
    )

    return {
        "total_cases": total,
        "passed": passed,
        "overall_accuracy": round(passed / total, 4) if total else 0.0,
        "in_scope_cases": len(in_scope),
        "in_scope_pass": sum(1 for r in in_scope if r["passed"]),
        "retrieval_recall_at_3": round(
            sum(1 for r in in_scope if r["passed"]) / len(in_scope), 4
        ) if in_scope else 0.0,
        "triage_cases": len(triage),
        "triage_pass": sum(1 for r in triage if r["passed"]),
        "out_of_scope_cases": len(out_scope),
        "out_of_scope_pass": sum(1 for r in out_scope if r["passed"]),
        "adversarial_cases": len(adversarial),
        "adversarial_pass": sum(1 for r in adversarial if r["passed"]),
        "pii_cases": len(pii),
        "pii_leak_rate": round(
            sum(1 for r in pii if r["leaked_pii"]) / len(pii), 4
        ) if pii else 0.0,
        "pii_masking_recall": round(
            1 - (
                sum(1 for r in pii if r["leaked_pii"]) / len(pii)
                if pii else 0.0
            ),
            4,
        ),
        "epistemic_routing_accuracy": round(
            sum(1 for r in labeled if r["resolution_mode"] == r["expected_mode"])
            / len(labeled),
            4,
        ) if labeled else 0.0,
        "actionable_guidance_completeness_rate": round(
            sum(1 for r in non_grounded if r["guidance_complete"])
            / len(non_grounded),
            4,
        ) if non_grounded else 0.0,
        "rewrite_recovery_rate": round(
            sum(1 for probe in probes if probe["passed"]) / len(probes), 4
        ) if probes else 0.0,
        "citations_emitted": citations_emitted,
        "citations_verified": citations_valid,
        "citation_validity": round(
            citations_valid / citations_emitted, 4
        ) if citations_emitted else 1.0,
        "claims_emitted": claims_emitted,
        "claims_verified": claims_valid,
        "claim_span_validity": round(
            claims_valid / claims_emitted, 4
        ) if claims_emitted else 1.0,
        "latency_p50_ms": latencies[len(latencies) // 2] if latencies else 0,
        "latency_p95_ms": p95,
        "resolution_mode_counts": dict(
            Counter(r["resolution_mode"] for r in results)
        ),
        "ai_status_counts": dict(
            Counter(r["ai_synthesis_status"] for r in results)
        ),
    }


def write_markdown(metrics, results, path):
    lines = [
        "# Pramana Evaluation Results",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "| Metric | Value |",
        "| :--- | :--- |",
    ]
    for key, value in metrics.items():
        lines.append(f"| {key} | {value} |")
    lines.extend([
        "",
        "## Case Results",
        "",
        "| Case | Category | Passed | Mode | Status | Guidance | Citations |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ])
    for result in results:
        citations = ", ".join(result["citation_ids"]) or "-"
        lines.append(
            f"| {result['id']} | {result['category']} | "
            f"{'PASS' if result['passed'] else 'FAIL'} | "
            f"{result['resolution_mode']} | {result['status']} | "
            f"{'complete' if result['guidance_complete'] else 'incomplete'} | "
            f"{citations} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--retrieval-only",
        action="store_true",
        help="Force AI_MODE=disabled for a deterministic retrieval baseline.",
    )
    parser.add_argument(
        "--mode",
        choices=("current", "fast", "live"),
        default="current",
        help="fast disables AI; live uses the configured AI key.",
    )
    args = parser.parse_args()

    if args.retrieval_only or args.mode == "fast":
        os.environ["AI_MODE"] = "disabled"

    from backend.services.ai_config import get_ai_mode, get_gemini_api_key
    from backend.services.rag_engine import StrictRAGEngine

    cases = load_cases()
    engine = StrictRAGEngine()
    results = []

    ai_active = (
        get_ai_mode() != "disabled" and bool(get_gemini_api_key())
    )
    for case in cases:
        results.append(run_case(engine, case, ai_active=ai_active))
        if ai_active:
            time.sleep(1.5)

    metrics = summarize(cases, results)
    metrics["ai_mode"] = get_ai_mode()
    metrics["ai_key_present"] = bool(get_gemini_api_key())

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "latest.json").write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "metrics": metrics,
                "results": results,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    write_markdown(metrics, results, RESULTS_DIR / "latest.md")

    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    return 0 if metrics["passed"] == metrics["total_cases"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
