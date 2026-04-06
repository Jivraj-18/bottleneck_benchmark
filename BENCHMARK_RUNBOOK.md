# BottleneckBench runbook

This repository now includes an executable benchmark runner:
- Script: run_bottleneck_bench.py
- Dependencies: requirements.txt

## What the script does

- Loads all 10 cases from:
  - bottleneckbench_recent_audit_reviews
  - bottleneckbench_recent_outages
- Runs each case in 2 prompt conditions:
  - baseline
  - treatment (adds the tested line)
- Runs 3 model lanes:
  - Claude Haiku directly via Anthropic API
  - GPT via AI Pipe OpenRouter endpoint
  - Gemini via AI Pipe OpenRouter endpoint
- Optionally scores each model output using Claude Sonnet and each case scoring checklist.

## End-to-end flow

1. Load all case folders from both datasets.
2. For each case, build 2 prompts:
  - baseline
  - treatment (same prompt plus the tested line)
  - while constructing the case packet in prompt, remove model_packet.task so the model gets only one instruction source
  - baseline wording is dataset-specific:
    - audit reviews use the audit protocol baseline phrasing
    - outages use the outage protocol baseline phrasing ("Analyze this outage case..." with numbered outputs)
3. For each prompt, run 3 target models:
  - GPT model via AI Pipe (OpenRouter endpoint)
  - Gemini model via AI Pipe (OpenRouter endpoint)
  - Claude Haiku directly via Anthropic API
4. Parse each model response as strict JSON in the required benchmark schema.
5. If scoring is enabled, send each parsed candidate output to Claude Sonnet judge.
6. Sonnet returns binary and graded scores, and the script computes totals.
7. Save all detailed records to JSONL and compact rows to CSV.

## Prompt templates used

### Audit reviews baseline

Analyze this case. Identify:
the main bottleneck, the slow variables, the top 3 interventions, 2 things to deprioritize, and the earliest warning signals that leadership should track.

### Audit reviews treatment

Analyze this case. Identify:
the main bottleneck, the slow variables, the top 3 interventions, 2 things to deprioritize, and the earliest warning signals that leadership should track.

Identify  the binding constraints and slow variables - What governs here regardless of improvements elsewhere?

### Outages baseline

Analyze this outage case. Identify:
1. the binding constraint,
2. the slow variables,
3. the top 3 interventions you would prioritize,
4. 2 interventions you would explicitly deprioritize,
5. 3 early-warning signals.

Be concrete and case-specific.

### Outages treatment

Analyze this outage case.

Identify  the binding constraints and slow variables - What governs here regardless of improvements elsewhere?

Then provide:
1. the binding constraint,
2. the slow variables,
3. the top 3 interventions you would prioritize,
4. 2 interventions you would explicitly deprioritize,
5. 3 early-warning signals.

Be concrete and case-specific.

### Output-format suffix applied to all prompts

Return JSON only. Do not include markdown or any extra text.
Use exactly this schema shape (with case-specific values):

{
  "binding_constraint": "string",
  "slow_variables": [
    "string",
    "string"
  ],
  "top_interventions": [
    {
      "action": "string",
      "why": "string"
    },
    {
      "action": "string",
      "why": "string"
    },
    {
      "action": "string",
      "why": "string"
    }
  ],
  "deprioritize": [
    "string",
    "string"
  ],
  "early_warning_signals": [
    "string",
    "string",
    "string"
  ]
}

## What Sonnet receives (judge input)

For every model answer, Sonnet gets a single scoring prompt that includes:

- case_id
- scoring_checklist.json for that case (binary checks + graded anchors)
- gold_packet.json for that case (reference quality anchors)
- the candidate model output JSON (the answer produced by GPT/Gemini/Haiku)
- strict output schema Sonnet must follow

Sonnet is instructed to return JSON only with:

- binary_checks: 5 values, each 0 or 1, in checklist order
- graded_checks: 4 values, each integer 0 to 2
- evidence: short evidence snippets from candidate output
- confidence: float from 0 to 1

Then the script computes:

- total_binary = sum(binary_checks)
- total_graded = sum(graded_checks)
- total_score = total_binary + total_graded

Note: Sonnet does not receive baseline/treatment labels as a scoring category. It scores only the candidate content against that case rubric.

## Required .env keys

Use .env in repository root with:

CLAUDE_API_KEY=...
AIPIPE_API_KEY=...

## Install

python3 -m pip install -r requirements.txt

## Run all 10 cases once (recommended)

uv run python run_bottleneck_bench.py \
  --gpt-model openai/gpt-5.4-mini \
  --gemini-model google/gemini-3-flash-preview \
  --claude-provider claude_direct \
  --claude-model claude-haiku-4-5-20251001 \
  --judge-provider claude_direct \
  --judge-model claude-sonnet-4-6

## Smoke test on 1 case

uv run python run_bottleneck_bench.py \
  --max-cases 1 \
  --repeats 1 \
  --gpt-model openai/gpt-5.4-mini \
  --gemini-model google/gemini-3-flash-preview \
  --claude-provider claude_direct \
  --claude-model claude-haiku-4-5-20251001 \
  --judge-provider claude_direct \
  --judge-model claude-sonnet-4-6

Note: In this setup, Claude generation and Sonnet judging are run via direct Anthropic API.

## Useful options

- Repeats per cell (for variance):
  --repeats 3

- Limit case count during testing:
  --max-cases 1

- Disable Sonnet scoring pass:
  --skip-judge

- Choose provider for Claude generation lane:
  --claude-provider claude_direct|aipipe_openrouter

- Choose provider for Sonnet judge lane:
  --judge-provider claude_direct|aipipe_openrouter

## Outputs

Each run writes to a new timestamped directory under:
- benchmark_outputs

Files generated:
- results.jsonl: full per-run records, raw provider responses, parsed candidate JSON, judge scores
- errors.jsonl: failures with context
- summary.csv: compact table for analysis

summary.csv includes:
- total_score, total_binary, total_graded
- binary_check_1..binary_check_5
- binding_constraint_accuracy_0_to_2
- slow_variable_recall_0_to_2
- intervention_quality_0_to_2
- distractor_resistance_0_to_2
- judge_confidence, judge_error

Each row in results.jsonl retains the full call artifacts for that run:
- prompt: exact prompt sent to the model
- raw_text: model's plain-text response body extracted by the runner
- candidate_output: parsed JSON used for scoring
- provider_raw: raw API response payload from Anthropic or AI Pipe/OpenRouter
- judge: Sonnet scoring output and raw judge API payload (when judge is enabled)

## About AI Pipe usage

The script uses AI Pipe OpenRouter proxy endpoint for both GPT and Gemini lanes:
- URL: https://aipipe.org/openrouter/v1/chat/completions
- Header: Authorization: Bearer <AIPIPE_API_KEY>

This follows AI Pipe docs and uses OpenRouter-style model IDs such as openai/... and google/....
