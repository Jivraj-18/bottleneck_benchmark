# Evaluation protocol

## Recommended prompt setup

Use the same task framing in both conditions.

### Baseline
Analyze this case. Identify:
1. the main binding constraint or bottleneck,
2. the slow variables,
3. the top 3 interventions you would prioritize,
4. 2 interventions you would explicitly deprioritize,
5. 3 early-warning signals leadership should track.

Be concrete and case-specific.

### Treatment
Use the exact same prompt, plus:

> Identify the binding constraints and slow variables — what governs here regardless of improvements elsewhere?

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
- binding-constraint accuracy
- slow-variable recall
- intervention quality
- distractor resistance
- early-warning usefulness

## Optional robustness checks

Create:
- paraphrased case variants
- reordered case variants
- compressed case variants
- distractor-inflated variants
- domain-skinned structural variants

## Important caution

Because these are public reports, treat them as a development set.
For a stronger final benchmark, keep a private held-out set built the same way from newer or internal reports.
