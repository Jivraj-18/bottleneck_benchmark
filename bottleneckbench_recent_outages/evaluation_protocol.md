# Evaluation protocol

## Target fragment

> Identify the binding constraints and slow variables — what governs here regardless of improvements elsewhere?

## Baseline prompt

Analyze this outage case. Identify:
1. the binding constraint,
2. the slow variables,
3. the top 3 interventions you would prioritize,
4. 2 interventions you would explicitly deprioritize,
5. 3 early-warning signals.

Be concrete and case-specific.

## Treatment prompt

Analyze this outage case.

Identify the **binding constraints and slow variables — what governs here regardless of improvements elsewhere?**

Then provide:
1. the binding constraint,
2. the slow variables,
3. the top 3 interventions you would prioritize,
4. 2 interventions you would explicitly deprioritize,
5. 3 early-warning signals.

Be concrete and case-specific.

## Recommended output schema

```json
{
  "binding_constraint": "...",
  "slow_variables": ["...", "..."],
  "top_interventions": [
    {"action": "...", "why": "..."},
    {"action": "...", "why": "..."},
    {"action": "...", "why": "..."}
  ],
  "deprioritize": ["...", "..."],
  "early_warning_signals": ["...", "...", "..."]
}
```

## Suggested scoring

Use the per-case `scoring_checklist.json` plus the gold packet.

Recommended top-line metrics:
- binding constraint accuracy
- slow variable recall
- intervention quality
- distractor resistance
- early-warning usefulness

## Important caution

These are all public reports, so they are best for:
- development
- prompt comparison
- evaluator debugging

They are **not** suitable as a hidden final benchmark set.
