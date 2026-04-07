# Evaluation protocol

## Recommended prompt setup

Use the same task framing in both conditions. Example:

### Baseline
Analyze this case. Identify the main bottleneck, the slow variables, the top 3 interventions, 2 things to deprioritize, and the earliest warning signals that leadership should track.

### Treatment
Same as baseline, plus:
Identify the binding constraints and slow variables — what governs here regardless of improvements elsewhere?

## Output format

Ask the model to return JSON with:
- binding_constraint
- slow_variables[]
- top_interventions[]
- deprioritize[]
- early_warning_signals[]

## Scoring

For each case:
- score against `scoring_checklist.json`
- use binary checks first
- then use the 0–2 graded checks

## Recommended metrics

- Bottleneck accuracy
- Slow-variable recall
- Intervention quality
- Distractor resistance
- Early-warning usefulness

## Robustness checks

If you want a stronger benchmark, create:
- paraphrased case variants
- reordered case variants
- compressed case variants
- distractor-inflated variants

## Caution

Because these are public cases, treat them as a development set.
For a stronger final benchmark, keep a private held-out set built the same way from newer or internal reports.
