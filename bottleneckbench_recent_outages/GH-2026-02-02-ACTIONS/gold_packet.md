# GitHub Actions outage from provider policy change blocking VM metadata — Gold packet

## Binding Constraint Top1

A provider-side backend storage access policy change blocked critical VM metadata access, breaking VM lifecycle operations that Actions hosted runners depend on globally.

## Binding Constraint Top3

- Hidden single point of failure in provider metadata/control dependency for hosted-runner lifecycle operations
- Insufficient isolation/failover away from a provider-wide metadata/control-plane failure

## Slow Variables

- Provider dependency architecture and cross-region blast-radius assumptions
- Safe rollout and early detection for provider policy changes
- Incident-response and escalation paths with the underlying compute provider

## Contributing Factors

- The failure was global, not regional, because the policy change affected backend storage accounts broadly.
- Dependent features sharing the same compute substrate were affected too.
- Even after rollback, backlog drain extended perceived recovery.

## Good Interventions Ranked

- Improve isolation and failover assumptions around provider metadata/control dependencies for runner lifecycle operations.
- Work with the provider on safer rollout and earlier detection of backend policy changes before customer impact.
- Reduce dependency coupling so secondary features do not all fail when hosted-runner VM lifecycle operations are blocked.

## Bad Interventions

- Adding more runner capacity without addressing metadata/control-plane dependency
- Application-layer tuning for Actions queue handling as the main fix
- Focusing only on customer messaging

## Early Warning Signals

- Cross-region spikes in VM create/delete/reimage failures
- Hosted-runner wait times rising globally while self-hosted runners remain healthy
- Provider telemetry/policy changes touching backend storage or metadata access

## Distractors To Penalize

- Generic CI performance optimization
- Code-level changes in Actions workflows
- Scaling Pages/Copilot independently

## Evidence

- The report says a backend storage access policy change blocked critical VM metadata access.
- Hosted runners across all regions were affected; self-hosted runners on other providers were not.
