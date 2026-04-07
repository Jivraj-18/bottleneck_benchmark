# BottleneckBench Runbook

## Install

```bash
python3 -m pip install -r requirements.txt
```

## Required .env keys

```bash
CLAUDE_API_KEY=...
AIPIPE_API_KEY=...
```

## prompt_templates.json format

```json
{
	"baseline": "...",
	"treatment": "..."
}
```

## Script inputs and formats

Required command inputs:
- --cases-dir: Path to one dataset directory that contains case subfolders.
- --prompt-config: Path to prompt config JSON with baseline and treatment strings.

Common optional command inputs:
- --root: Repo root (default: .)
- --output-dir: Output folder for per-run JSONL files (default: benchmark_outputs)
- --repeats: Number of repeats per case/model/condition (default: 1)
- --max-cases: Limit number of discovered cases, 0 means all (default: 0)
- --skip-judge: Skip Sonnet judge scoring
- --gpt-model: GPT model id for AI Pipe/OpenRouter lane
- --gemini-model: Gemini model id for AI Pipe/OpenRouter lane
- --claude-model: Claude Haiku model id for generation lane
- --judge-model: Claude Sonnet model id for judge lane
- --claude-provider: claude_direct or aipipe_openrouter
- --judge-provider: claude_direct or aipipe_openrouter

Expected --cases-dir structure:

Each immediate subfolder under --cases-dir is treated as one case only if all 3 files exist:
- model_packet.json
- scoring_checklist.json
- gold_packet.json

Example layout:

```text
bottleneckbench_recent_outages/
  CASE-EXAMPLE-1/
    model_packet.json
    scoring_checklist.json
    gold_packet.json
  CASE-EXAMPLE-2/
    model_packet.json
    scoring_checklist.json
    gold_packet.json
```

Minimum JSON expectations:
- model_packet.json: Any valid JSON object. case_id is recommended.
- scoring_checklist.json: Any valid JSON object used by the judge prompt.
- gold_packet.json: Any valid JSON object used as reference in judging.

Example model_packet.json:

```json
{
	"case_id": "CASE-EXAMPLE-1",
	"title": "Short case title",
	"context": "Case narrative and evidence"
}
```

Example scoring_checklist.json:

```json
{
	"case_id": "CASE-EXAMPLE-1",
	"checks": [
		"Identifies the binding constraint",
		"Names slow variables",
		"Proposes interventions"
	]
}
```

Example gold_packet.json:

```json
{
	"case_id": "CASE-EXAMPLE-1",
	"gold_answer": {
		"binding_constraint": "...",
		"slow_variables": ["..."],
		"interventions": ["...", "...", "..."]
	}
}
```

## Run

Run once per dataset directory:

```bash
uv run python run_bottleneck_bench.py \
	--cases-dir bottleneckbench_recent_outages \
	--prompt-config prompt_templates.json \
	--gpt-model gpt-5.4-mini \
	--gemini-model google/gemini-3-flash-preview \
	--claude-provider claude_direct \
	--claude-model claude-haiku-4-5-20251001 \
	--judge-provider claude_direct \
	--judge-model claude-sonnet-4-6
```

Swap --cases-dir for each dataset:
- bottleneckbench_recent_outages
- bottleneckbench_recent_audit_reviews

## Smoke test (1 case)

```bash
uv run python run_bottleneck_bench.py \
	--cases-dir bottleneckbench_recent_outages \
	--prompt-config prompt_templates.json \
	--max-cases 1 \
	--repeats 1 \
	--gpt-model gpt-5.4-mini \
	--gemini-model google/gemini-3-flash-preview \
	--claude-provider claude_direct \
	--claude-model claude-haiku-4-5-20251001 \
	--judge-provider claude_direct \
	--judge-model claude-sonnet-4-6
```

## Outputs

| File | Contents |
|---|---|
| benchmark_outputs/<timestamp>/results.jsonl | Full per-case results |
| benchmark_outputs/<timestamp>/errors.jsonl | Errors |
| summary.csv | Scores per case and model |