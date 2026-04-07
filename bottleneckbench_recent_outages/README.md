# Recent outage case studies for BottleneckBench

This package contains **5 recent, public outage reports** (published in February–March 2026) converted into benchmark-ready case studies for the prompt fragment:

> Identify the binding constraints and slow variables — what governs here regardless of improvements elsewhere?

Each case includes:
- `model_packet.md` / `model_packet.json`: the blinded packet you can give to a model
- `gold_packet.md` / `gold_packet.json`: the answer key for evaluation
- `scoring_checklist.json`: binary / checklist-oriented evaluation prompts
- `source_metadata.json`: source URL, publication date, and selection notes

## Notes

- These are best used as **public development-set items**, not hidden final-test items.
- The model packets intentionally omit or blur the explicit root-cause section when possible.
- The gold packets are tuned for a **binding-constraint / slow-variable** benchmark, not generic incident-summary evaluation.

## Suggested evaluation

For each case, run:
1. A baseline prompt
2. The same prompt + the target fragment

Then score:
- binding-constraint accuracy
- slow-variable recall
- intervention quality
- distractor resistance
- early-warning usefulness

A machine-readable summary is in `cases_manifest.csv`.
