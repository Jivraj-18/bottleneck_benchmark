# Cloudflare BYOIP prefix withdrawal outage — Model packet

## Background

A major edge/network provider experienced an outage that affected a subset of customers using a service that lets them bring their own IP ranges. Some customer services became unreachable from the Internet, causing timeouts and connection failures. The provider's recursive DNS website also saw 403 errors.

## System Context

- The affected service manages customer IP prefixes and their advertisement to the Internet.
- Customer changes are persisted in an authoritative database, and the same database is used for operational actions.
- Customers can sometimes self-mitigate by re-advertising their prefixes via a dashboard.
- A release related to the addressing API completed shortly before impact began.

## Timeline

- 2026-02-05 21:53 UTC: code related to the later incident was merged.
- 2026-02-20 17:46 UTC: release completed.
- 2026-02-20 17:56 UTC: impact began as prefix advertisement updates started propagating; prefixes began to be withdrawn.
- 2026-02-20 18:13 UTC: provider engaged for failures on a high-visibility internal service.
- 2026-02-20 18:18 UTC: internal incident declared.
- 2026-02-20 18:21 UTC: engineering team responsible for the addressing API paged.
- 2026-02-20 18:46 UTC: team identified the issue and disabled the problematic execution path.
- 2026-02-20 19:11 UTC onward: teams worked on restoring serviceability for withdrawn and removed prefixes.
- 2026-02-20 19:19 UTC: some customers began re-advertising prefixes via dashboard, partially reducing impact.
- 2026-02-20 23:03 UTC: global configuration rollout completed; incident ended.

## Observations

- Roughly 1,100 customer prefixes were withdrawn before the team was able to revert the change.
- Most of the total incident duration was spent restoring prefix configurations to their prior state.
- Rollback and recovery were harder because desired customer configuration and operational state were tightly coupled.
- The provider later emphasized the need for controlled rollouts, rollback mechanisms, and broad-change circuit breakers.

## Task

Identify the binding constraint and slow variables. What governed the severity and duration of this incident regardless of improvements elsewhere? Recommend the top 3 interventions and 2 things you would explicitly deprioritize.
