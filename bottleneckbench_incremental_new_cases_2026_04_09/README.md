# BottleneckBench incremental package: 10 new public development cases

This package contains **only the newly added cases** requested in the latest expansion:
- **5 new recent software outage postmortems**
- **5 new recent audit / program-review reports**

These are formatted as benchmark-ready BottleneckBench case studies for the prompt fragment:

> Identify the binding constraints and slow variables — what governs here regardless of improvements elsewhere?

## What is included

For each case:
- `source_metadata.json` — source title, publisher, publication date, URL, geography, and short notes
- `model_packet.json` / `model_packet.md` — the **blinded** packet intended for the model
- `gold_packet.json` / `gold_packet.md` — the benchmark answer key
- `scoring_checklist.json` — a light rubric for fast scoring

At the top level:
- `cases_manifest.csv` — one row per case
- `combined_cases.json` — all 10 cases in one file
- `evaluation_protocol.md` — suggested evaluation protocol

## Important caveat

These are **public development cases**, not a hidden final benchmark.
The source reports are public and recent. They are useful for:
- early benchmark design
- prompt-fragment comparisons
- scoring-rubric refinement

They are **not** ideal as a final held-out test, because a model may have seen the source documents.

Created on 2026-04-09.
