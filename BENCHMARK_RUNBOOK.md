# BottleneckBench runbook

This repository includes an executable benchmark runner:
- Script: run_bottleneck_bench.py
- Dependencies: requirements.txt

## What the script does

- Loads cases from one explicit directory via --cases-dir
- Runs each case in 2 prompt conditions: baseline and treatment
- Loads baseline/treatment text from a standalone prompt config file (--prompt-config)
- Runs 3 model lanes:
  - Claude Haiku via Anthropic API
  - GPT via AI Pipe OpenRouter
  - Gemini via AI Pipe OpenRouter
- Optionally scores each model output using Claude Sonnet and the case checklist.

## End-to-end flow

1. Load case folders from --cases-dir.
2. Load prompt templates from --prompt-config.
3. Build baseline/treatment prompts from that config.
4. Remove model_packet.task from case packet before prompting to avoid instruction collisions.
5. Run models for each case and condition.
6. Parse model JSON output.
7. Score with Sonnet judge (optional).
8. Write detailed JSONL artifacts and summary CSV.

## Prompt config

Prompt templates are loaded from a separate JSON file, not from case directories.

Default path:
- prompt_templates.json (repo root)

Required format:

```json
{
  "baseline": "...",
  "treatment": "..."
}
```

## Shared output suffix

The runner appends this instruction to all prompts:
- Return JSON only. Do not include markdown or any extra text.
- Use the required schema:

```json
{
  "binding_constraint": "string",
  "slow_variables": ["string", "string"],
  "top_interventions": [
    {"action": "string", "why": "string"},
    {"action": "string", "why": "string"},
    {"action": "string", "why": "string"}
  ],
  "deprioritize": ["string", "string"],
  "early_warning_signals": ["string", "string", "string"]
}
```

## Sonnet judge input

For every candidate output, Sonnet receives:
- case_id
- scoring_checklist.json
- gold_packet.json
- candidate model output JSON
- strict judge output schema

## Required .env keys

```bash
CLAUDE_API_KEY=...
AIPIPE_API_KEY=...
```

## Install

```bash
python3 -m pip install -r requirements.txt
```

## Run (all cases in one directory)

```bash
uv run python run_bottleneck_bench.py \
  --cases-dir bottleneckbench_recent_outages \
  --prompt-config prompt_templates.json \
  --gpt-model openai/gpt-5.4-mini \
  --gemini-model google/gemini-3-flash-preview \
  --claude-provider claude_direct \
  --claude-model claude-haiku-4-5-20251001 \
  --judge-provider claude_direct \
  --judge-model claude-sonnet-4-6
```

Run once per dataset directory:
- outages: --cases-dir bottleneckbench_recent_outages
- audits: --cases-dir bottleneckbench_recent_audit_reviews

## Smoke test (1 case)

```bash
uv run python run_bottleneck_bench.py \
  --cases-dir bottleneckbench_recent_outages \
  --prompt-config prompt_templates.json \
  --max-cases 1 \
  --repeats 1 \
  --gpt-model openai/gpt-5.4-mini \
  --gemini-model google/gemini-3-flash-preview \
  --claude-provider claude_direct \
  --claude-model claude-haiku-4-5-20251001 \
  --judge-provider claude_direct \
  --judge-model claude-sonnet-4-6
```

## Required cases-dir format

```text
path/to/cases_directory/
  CASE-1/
    model_packet.json
    scoring_checklist.json
    gold_packet.json
  CASE-2/
    model_packet.json
    scoring_checklist.json
    gold_packet.json
```

Required alongside cases-dir (outside that directory):
- prompt config file (default `prompt_templates.json` in repo root, or pass `--prompt-config`)

Optional files:
- model_packet.md
- gold_packet.md
- source_metadata.json

## Useful options

- --repeats 3
- --max-cases 1
- --skip-judge
- --prompt-config path/to/prompt_templates.json
- --claude-provider claude_direct|aipipe_openrouter
- --judge-provider claude_direct|aipipe_openrouter

## Outputs

- benchmark_outputs/<timestamp>/results.jsonl
- benchmark_outputs/<timestamp>/errors.jsonl
- summary.csv (repo root)

summary.csv includes:
- total_score, total_binary, total_graded
- binary_check_1..binary_check_5
- binding_constraint_accuracy_0_to_2
- slow_variable_recall_0_to_2
- intervention_quality_0_to_2
- distractor_resistance_0_to_2
- judge_confidence, judge_error
