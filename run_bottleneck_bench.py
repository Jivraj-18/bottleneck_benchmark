#!/usr/bin/env python3
"""Run BottleneckBench across models and prompt conditions.

- Claude Haiku is called directly via Anthropic API.
- GPT and Gemini are called via AI Pipe OpenRouter proxy.
- Optional Claude Sonnet judge scores each model output against per-case rubric.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv


ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
AIPIPE_OPENROUTER_URL = "https://aipipe.org/openrouter/v1/chat/completions"

OUTPUT_SCHEMA = {
    "binding_constraint": "string",
    "slow_variables": ["string", "string"],
    "top_interventions": [
        {"action": "string", "why": "string"},
        {"action": "string", "why": "string"},
        {"action": "string", "why": "string"},
    ],
    "deprioritize": ["string", "string"],
    "early_warning_signals": ["string", "string", "string"],
}

@dataclass
class ModelSpec:
    name: str
    provider: str  # claude_direct | aipipe_openrouter
    model: str


@dataclass
class CaseSpec:
    case_id: str
    source_root: str
    model_packet: dict[str, Any]
    scoring_checklist: dict[str, Any]
    gold_packet: dict[str, Any]


@dataclass
class PromptTemplates:
    baseline: str
    treatment: str


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def list_cases(root: Path) -> list[CaseSpec]:
    cases: list[CaseSpec] = []

    for item in sorted(root.iterdir()):
        if not item.is_dir():
            continue

        model_packet_file = item / "model_packet.json"
        scoring_file = item / "scoring_checklist.json"
        gold_file = item / "gold_packet.json"
        if not (model_packet_file.exists() and scoring_file.exists() and gold_file.exists()):
            continue

        model_packet = load_json(model_packet_file)
        scoring = load_json(scoring_file)
        gold = load_json(gold_file)

        case_id = str(model_packet.get("case_id") or scoring.get("case_id") or item.name)
        cases.append(
            CaseSpec(
                case_id=case_id,
                source_root=root.name,
                model_packet=model_packet,
                scoring_checklist=scoring,
                gold_packet=gold,
            )
        )
    return cases


def load_prompt_templates(config_path: Path) -> PromptTemplates:
    if not config_path.exists():
        raise FileNotFoundError(
            f"Missing prompt template config: {config_path}. "
            "Create prompt_templates.json with baseline and treatment fields."
        )

    cfg = load_json(config_path)
    baseline = str(cfg.get("baseline", "")).strip()
    treatment = str(cfg.get("treatment", "")).strip()

    if not baseline or not treatment:
        raise ValueError(
            f"Invalid prompt_templates.json at {config_path}. "
            "Both 'baseline' and 'treatment' must be non-empty strings."
        )

    return PromptTemplates(baseline=baseline, treatment=treatment)


def extract_json_block(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()

    if text.startswith("{") and text.endswith("}"):
        return text

    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        return match.group(0)

    raise ValueError("No JSON object found in model output")


def parse_candidate_output(text: str) -> dict[str, Any]:
    block = extract_json_block(text)
    return json.loads(block)


def build_prompt_packet(model_packet: dict[str, Any]) -> dict[str, Any]:
    """Return a prompt-safe packet without embedded task instructions.

    The runner provides a single canonical task prompt, so we drop any existing
    case-level task field to avoid mixed or contradictory directions.
    """
    packet = dict(model_packet)
    packet.pop("task", None)
    return packet


def build_task_instruction(prompt_templates: PromptTemplates, condition: str) -> str:
    if condition == "baseline":
        return prompt_templates.baseline
    if condition == "treatment":
        return prompt_templates.treatment
    raise ValueError(f"Unknown condition: {condition}")


def build_case_prompt(case: CaseSpec, condition: str, prompt_templates: PromptTemplates) -> str:
    task = build_task_instruction(prompt_templates, condition)

    prompt_packet = build_prompt_packet(case.model_packet)

    return (
        "You are analyzing a BottleneckBench case packet.\n"
        f"Case ID: {case.case_id}\n\n"
        "Case packet (JSON):\n"
        f"{json.dumps(prompt_packet, indent=2, ensure_ascii=True)}\n\n"
        f"{task}\n\n"
        "Return JSON only. Do not include markdown or any extra text.\n"
        "Use exactly this schema shape (with case-specific values):\n"
        f"{json.dumps(OUTPUT_SCHEMA, indent=2)}"
    )


def call_claude(api_key: str, model: str, prompt: str, max_tokens: int = 1400) -> tuple[str, dict[str, Any]]:
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": 0,
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = requests.post(ANTHROPIC_URL, headers=headers, json=payload, timeout=120)
    try:
        resp.raise_for_status()
    except requests.HTTPError as exc:
        raise RuntimeError(f"Anthropic HTTP {resp.status_code}: {resp.text[:1200]}") from exc
    data = resp.json()

    chunks = data.get("content", [])
    text = "".join(c.get("text", "") for c in chunks if c.get("type") == "text")
    if not text:
        raise RuntimeError(f"No text content from Claude response: {data}")
    return text, data


def call_aipipe_openrouter(api_key: str, model: str, prompt: str, max_tokens: int = 1400) -> tuple[str, dict[str, Any]]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": max_tokens,
    }
    resp = requests.post(AIPIPE_OPENROUTER_URL, headers=headers, json=payload, timeout=120)
    try:
        resp.raise_for_status()
    except requests.HTTPError as exc:
        raise RuntimeError(f"AI Pipe OpenRouter HTTP {resp.status_code}: {resp.text[:1200]}") from exc
    data = resp.json()

    choices = data.get("choices", [])
    if not choices:
        raise RuntimeError(f"No choices in AI Pipe response: {data}")

    text = choices[0].get("message", {}).get("content", "")
    if isinstance(text, list):
        # Some providers may return list fragments.
        text = "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in text)
    if not isinstance(text, str) or not text.strip():
        raise RuntimeError(f"No usable text in AI Pipe OpenRouter response: {data}")
    return text, data


def call_model(spec: ModelSpec, prompt: str, claude_key: str, aipipe_key: str) -> tuple[str, dict[str, Any]]:
    if spec.provider == "claude_direct":
        if not claude_key:
            raise RuntimeError("CLAUDE_API_KEY is missing")
        return call_claude(claude_key, spec.model, prompt)

    if spec.provider == "aipipe_openrouter":
        if not aipipe_key:
            raise RuntimeError("AIPIPE_API_KEY is missing")
        return call_aipipe_openrouter(aipipe_key, spec.model, prompt)

    raise ValueError(f"Unknown provider: {spec.provider}")


def build_judge_prompt(case: CaseSpec, candidate: dict[str, Any]) -> str:
    checklist = case.scoring_checklist
    graded = list(checklist.get("graded_checks", {}).keys())

    judge_schema = {
        "binary_checks": [0, 0, 0, 0, 0],
        "graded_checks": {
            graded[0] if len(graded) > 0 else "binding_constraint_accuracy_0_to_2": 0,
            graded[1] if len(graded) > 1 else "slow_variable_recall_0_to_2": 0,
            graded[2] if len(graded) > 2 else "intervention_quality_0_to_2": 0,
            graded[3] if len(graded) > 3 else "distractor_resistance_0_to_2": 0,
        },
        "evidence": ["brief evidence quote 1", "brief evidence quote 2"],
        "confidence": 0.0,
    }

    return (
        "You are a strict BottleneckBench evaluator.\n"
        "Score candidate output against the provided checklist and grading anchors.\n"
        "Use only the candidate output content for evidence.\n"
        "Return JSON only with the exact schema keys shown.\n"
        "Rules:\n"
        "- binary_checks must be 0 or 1 for each checklist item in order.\n"
        "- graded checks must be integers in [0,2].\n"
        "- confidence must be in [0,1].\n"
        "- Do not add extra keys.\n\n"
        f"Case ID: {case.case_id}\n\n"
        "Scoring checklist:\n"
        f"{json.dumps(case.scoring_checklist, indent=2, ensure_ascii=True)}\n\n"
        "Gold packet (for reference quality anchors):\n"
        f"{json.dumps(case.gold_packet, indent=2, ensure_ascii=True)}\n\n"
        "Candidate output JSON:\n"
        f"{json.dumps(candidate, indent=2, ensure_ascii=True)}\n\n"
        "Output schema:\n"
        f"{json.dumps(judge_schema, indent=2)}"
    )


def score_with_judge(
    case: CaseSpec,
    candidate: dict[str, Any],
    claude_key: str,
    aipipe_key: str,
    judge_provider: str,
    judge_model: str,
) -> dict[str, Any]:
    prompt = build_judge_prompt(case, candidate)
    if judge_provider == "claude_direct":
        text, raw = call_claude(claude_key, judge_model, prompt, max_tokens=1200)
    elif judge_provider == "aipipe_openrouter":
        text, raw = call_aipipe_openrouter(aipipe_key, judge_model, prompt, max_tokens=1200)
    else:
        raise ValueError(f"Unknown judge provider: {judge_provider}")
    parsed = parse_candidate_output(text)

    binary = parsed.get("binary_checks", [])
    graded = parsed.get("graded_checks", {})

    total_binary = int(sum(int(x) for x in binary))
    total_graded = int(sum(int(v) for v in graded.values()))

    parsed["total_binary"] = total_binary
    parsed["total_graded"] = total_graded
    parsed["total_score"] = total_binary + total_graded
    parsed["_raw_response"] = raw
    return parsed


def ensure_output_dir(base: Path) -> Path:
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    out = base / f"benchmark_run_{stamp}"
    out.mkdir(parents=True, exist_ok=False)
    return out


def build_summary_row(record: dict[str, Any]) -> dict[str, Any]:
    row = {
        "case_id": record.get("case_id", ""),
        "source_root": record.get("source_root", ""),
        "model_name": record.get("model_name", ""),
        "model_id": record.get("model_id", ""),
        "condition": record.get("condition", ""),
        "run_id": record.get("run_id", ""),
        "total_score": record.get("total_score", ""),
        "total_binary": record.get("total_binary", ""),
        "total_graded": record.get("total_graded", ""),
        "binary_check_1": "",
        "binary_check_2": "",
        "binary_check_3": "",
        "binary_check_4": "",
        "binary_check_5": "",
        "binding_constraint_accuracy_0_to_2": "",
        "slow_variable_recall_0_to_2": "",
        "intervention_quality_0_to_2": "",
        "distractor_resistance_0_to_2": "",
        "judge_confidence": "",
        "judge_error": record.get("judge_error", ""),
    }

    judge = record.get("judge", {}) or {}
    binary = judge.get("binary_checks", []) or []
    graded = judge.get("graded_checks", {}) or {}

    for i in range(5):
        if i < len(binary):
            row[f"binary_check_{i + 1}"] = binary[i]

    row["binding_constraint_accuracy_0_to_2"] = graded.get("binding_constraint_accuracy_0_to_2", "")
    row["slow_variable_recall_0_to_2"] = graded.get("slow_variable_recall_0_to_2", "")
    row["intervention_quality_0_to_2"] = graded.get("intervention_quality_0_to_2", "")
    row["distractor_resistance_0_to_2"] = graded.get("distractor_resistance_0_to_2", "")
    row["judge_confidence"] = judge.get("confidence", "")
    return row


def main() -> int:
    parser = argparse.ArgumentParser(description="Run BottleneckBench across GPT/Gemini/Claude")
    parser.add_argument("--root", default=".", help="Repo root path")
    parser.add_argument("--cases-dir", required=True, help="Single directory containing case subfolders.")
    parser.add_argument(
        "--prompt-config",
        default="prompt_templates.json",
        help="Prompt config JSON path (relative to --root or absolute) with baseline/treatment.",
    )
    parser.add_argument("--output-dir", default="benchmark_outputs")
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--max-cases", type=int, default=0, help="0 = all")
    parser.add_argument("--skip-judge", action="store_true")

    parser.add_argument("--gpt-model", default="openai/gpt-5.4-mini")
    parser.add_argument("--gemini-model", default="google/gemini-3-flash-preview")
    parser.add_argument("--claude-model", default="claude-3-5-haiku-20241022")
    parser.add_argument("--judge-model", default="claude-3-5-sonnet-20241022")
    parser.add_argument(
        "--claude-provider",
        default="claude_direct",
        choices=["claude_direct", "aipipe_openrouter"],
        help="Provider for Claude Haiku generation lane",
    )
    parser.add_argument(
        "--judge-provider",
        default="claude_direct",
        choices=["claude_direct", "aipipe_openrouter"],
        help="Provider for Sonnet judge lane",
    )

    args = parser.parse_args()

    load_dotenv()
    claude_key = os.getenv("CLAUDE_API_KEY", "")
    aipipe_key = os.getenv("AIPIPE_API_KEY", "")

    root = Path(args.root).resolve()
    out_root = ensure_output_dir(root / args.output_dir)
    cases_root = root / args.cases_dir
    prompt_config = Path(args.prompt_config)
    if not prompt_config.is_absolute():
        prompt_config = root / prompt_config

    if not cases_root.exists():
        raise FileNotFoundError(f"Cases directory does not exist: {cases_root}")

    prompt_templates = load_prompt_templates(prompt_config)

    models = [
        ModelSpec(name="gpt", provider="aipipe_openrouter", model=args.gpt_model),
        ModelSpec(name="gemini", provider="aipipe_openrouter", model=args.gemini_model),
        ModelSpec(name="claude_haiku", provider=args.claude_provider, model=args.claude_model),
    ]

    conditions = ["baseline", "treatment"]

    all_cases = list_cases(cases_root)
    if args.max_cases > 0:
        all_cases = all_cases[: args.max_cases]

    if not all_cases:
        raise RuntimeError("No cases discovered. Check dataset folder paths.")

    results_jsonl = out_root / "results.jsonl"
    errors_jsonl = out_root / "errors.jsonl"
    summary_csv = root / "summary.csv"

    rows: list[dict[str, Any]] = []

    total_jobs = len(all_cases) * len(models) * len(conditions) * max(1, args.repeats)
    done = 0

    with results_jsonl.open("w", encoding="utf-8") as results_f, errors_jsonl.open("w", encoding="utf-8") as errors_f:
        for case in all_cases:
            for model in models:
                for condition in conditions:
                    for run_idx in range(1, args.repeats + 1):
                        done += 1
                        print(
                            f"[{done}/{total_jobs}] case={case.case_id} model={model.name} condition={condition} run={run_idx}",
                            flush=True,
                        )

                        record: dict[str, Any] = {
                            "timestamp": dt.datetime.now().isoformat(),
                            "case_id": case.case_id,
                            "source_root": case.source_root,
                            "model_name": model.name,
                            "model_id": model.model,
                            "condition": condition,
                            "run_id": run_idx,
                        }

                        try:
                            prompt = build_case_prompt(case, condition, prompt_templates)
                            record["prompt"] = prompt
                            answer_text, raw_response = call_model(model, prompt, claude_key, aipipe_key)
                            candidate = parse_candidate_output(answer_text)

                            record["candidate_output"] = candidate
                            record["raw_text"] = answer_text
                            record["provider_raw"] = raw_response

                            if not args.skip_judge:
                                if args.judge_provider == "claude_direct" and not claude_key:
                                    raise RuntimeError("CLAUDE_API_KEY is required for judge scoring")
                                if args.judge_provider == "aipipe_openrouter" and not aipipe_key:
                                    raise RuntimeError("AIPIPE_API_KEY is required for judge scoring via AIPipe")
                                try:
                                    judge = score_with_judge(
                                        case,
                                        candidate,
                                        claude_key,
                                        aipipe_key,
                                        args.judge_provider,
                                        args.judge_model,
                                    )
                                    record["judge"] = judge
                                    record["total_score"] = judge.get("total_score")
                                    record["total_binary"] = judge.get("total_binary")
                                    record["total_graded"] = judge.get("total_graded")
                                except Exception as judge_exc:  # noqa: BLE001
                                    record["judge_error"] = str(judge_exc)

                            rows.append(build_summary_row(record))

                            results_f.write(json.dumps(record, ensure_ascii=True) + "\n")
                            results_f.flush()

                        except Exception as exc:  # noqa: BLE001
                            err = {**record, "error": str(exc)}
                            errors_f.write(json.dumps(err, ensure_ascii=True) + "\n")
                            errors_f.flush()
                            print(f"  ERROR: {exc}", file=sys.stderr, flush=True)

                        time.sleep(0.2)

    with summary_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "case_id",
                "source_root",
                "model_name",
                "model_id",
                "condition",
                "run_id",
                "total_score",
                "total_binary",
                "total_graded",
                "binary_check_1",
                "binary_check_2",
                "binary_check_3",
                "binary_check_4",
                "binary_check_5",
                "binding_constraint_accuracy_0_to_2",
                "slow_variable_recall_0_to_2",
                "intervention_quality_0_to_2",
                "distractor_resistance_0_to_2",
                "judge_confidence",
                "judge_error",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print("\nRun complete.")
    print(f"Results: {results_jsonl}")
    print(f"Errors : {errors_jsonl}")
    print(f"Summary: {summary_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
