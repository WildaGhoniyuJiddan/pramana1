# Pramana Evaluation Harness

This directory contains the internal, reproducible evaluation set for Pramana.
It is **not** a public benchmark and must not be presented as one.

## Run

```bash
python eval/run_eval.py --retrieval-only
```

With `GEMINI_API_KEY` and `AI_MODE=required` (or `optional`):

```bash
python eval/run_eval.py
```

Results are written to:

- `eval/results/latest.json`
- `eval/results/latest.md`

## Case categories

| Category | Count | Purpose |
| :--- | :--- | :--- |
| `in_scope` | 20 | Tourism compliance and public-discourse questions with expected corpus citations |
| `out_of_scope` | 12 | Questions outside the corpus; must abstain |
| `adversarial` | 3 | Prompt injection and fabricated-law attempts |
| `pii` | 5 | Email, passport, booking code, card, phone masking |

## Metrics

- `retrieval_recall_at_3` — expected citation appears in top 3 retrieved chunks.
- `abstain_accuracy` — out-of-scope cases return `TIDAK_DITEMUKAN`.
- `pii_leak_rate` — raw PII tokens still present in masked output.
- `citation_validity` — emitted citations pass Layer-1 (the API only emits verified citations).
- `adversarial_pass` — no forbidden term in the AI output; AI-only abstain checks run when a key is active.
- `latency_p50_ms` / `latency_p95_ms` — measured per case.

## Important limitations

- The set is small and curated from the current corpus. A perfect score does not
  mean the system is universally accurate.
- The retrieval-only baseline does not exercise Gemini. AI metrics require a
  real API key and are reported only when the key is present.
- Citation validity is structurally enforced: an unverified citation is never
  returned. It is not a measure of whether the cited rule is the best answer.
- Do not publish these numbers as a public benchmark without a larger,
  independently labeled set.
