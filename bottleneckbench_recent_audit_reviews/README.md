# BottleneckBench recent audit / program review case studies

This package contains 5 recent public audit/program-review reports, converted into benchmark-ready cases for testing whether a model can identify **binding constraints** and **slow variables**.

## What is included

For each case:
- `source_metadata.json` — source title, publisher, publication date, URL, geography, and short notes
- `model_packet.json` / `model_packet.md` — the **blinded** packet intended for the model
- `gold_packet.json` / `gold_packet.md` — the benchmark answer key
- `scoring_checklist.json` — a light rubric for fast scoring

At the top level:
- `cases_manifest.csv` — one row per case
- `combined_cases.json` — all cases in one file
- `evaluation_protocol.md` — suggested evaluation protocol

## Important caveat

These are **public development cases**, not a hidden final benchmark.
The source reports are public and recent. They are useful for:
- early benchmark design
- prompt-fragment comparisons
- scoring-rubric refinement

They are **not** ideal as a final held-out test, because a model may have seen the source documents.

## Suggested use

Run each case in two conditions:
1. baseline diagnosis prompt
2. same prompt + the fragment:

> Identify the binding constraints and slow variables — what governs here regardless of improvements elsewhere?

Compare:
- bottleneck accuracy
- slow-variable recall
- intervention quality
- distractor resistance
- early-warning quality

Created on 2026-04-01.
