# Clerk outage from failed Cloud SQL live migration — Gold packet

## Binding Constraint Top1

Dependence on opaque live migration behavior in the managed database provider, whose failure mode caused severe disk latency and lock contention despite the database remaining nominally 'up'.

## Binding Constraint Top3

- Lack of control over a catastrophic provider maintenance path
- Architecture/operational dependence on live migration as a maintenance primitive

## Slow Variables

- Provider/platform choice and degree of operational control
- Database maintenance/failover strategy
- Ability to opt out of risky managed-provider behaviors
- Error translation and reliability hardening around provider-induced degradation

## Contributing Factors

- A failed live migration caused increased disk latency, which increased lock contention and saturated compute.
- The usual signs were misleading: CPU was normal and reads-vs-writes looked odd, delaying confident diagnosis.
- Replica-read offloading did not help because the underlying bottleneck was infrastructure-level disk latency during migration.

## Good Interventions Ranked

- Avoid or disable live migrations; use planned replica promotion / explicit maintenance workflows instead.
- Re-pin or otherwise constrain provider maintenance until the unsafe migration mode is eliminated.
- Evaluate migrating to a different database provider or self-operating Postgres if the risky maintenance behavior cannot be turned off.

## Bad Interventions

- Adding more database CPU
- Read-replica scaling alone
- Tuning only query/application performance while leaving live-migration risk intact

## Early Warning Signals

- Read-side IO wait spikes without matching write increase
- Lock contention spikes with normal CPU
- Previous incident history showing that provider live-migration failures have catastrophic behavior

## Distractors To Penalize

- General app-layer optimization
- Replica count increases as the primary fix
- Treating this as a generic traffic surge

## Evidence

- The postmortem attributes the outage to a failed Google Cloud SQL live migration.
- The company concluded that if live migrations cannot be disabled, it may need another provider or in-house operation.
