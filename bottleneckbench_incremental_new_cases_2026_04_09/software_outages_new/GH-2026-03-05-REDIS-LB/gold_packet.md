# Gold packet — GH-2026-03-05-REDIS-LB

## Binding constraint (top 1)
Configuration safety and validation around critical Redis / load-balancer infrastructure changes, where a bad internal-routing change can stall the Actions control path and create a large queue backlog.

## Acceptable top-3 near-equivalents
- Unsafe propagation of infrastructure config changes into Redis / load-balancer control planes
- Lack of guardrails preventing misrouted internal traffic in critical queueing infrastructure
- Weak pre-deployment validation and blast-radius control for resiliency-layer changes

## Slow variables
- Infrastructure configuration management and change validation
- Automated policy checks that block invalid load-balancer routing
- Client resiliency to brief cache / routing interruptions
- Backlog-recovery planning for high-throughput workflow queues

## Contributing factors
- Incorrect configuration changes were introduced into the Redis load balancer
- Internal traffic was routed to the wrong host
- The change was part of a production rollout in critical infrastructure
- Residual user pain persisted through queue draining after the immediate routing fix

## Good interventions (ranked)
1. Add automated configuration validation and policy enforcement that blocks unsafe Redis/load-balancer changes before production.
2. Reduce blast radius for critical infra updates through narrower canaries, staged rollout, and fast auto-abort criteria.
3. Improve Actions client and queue-path resiliency so short cache/routing interruptions do not become long workflow delays.

## Bad / deprioritized interventions
- Only improving queue-drain speed after incidents
- Treating the problem as merely a Redis capacity issue
- Relying on manual alert triage without stronger config-prevention controls

## Early-warning signals
- Load-balancer config diffs that introduce unexpected target-host mappings
- Sharp rise in workflows not starting within SLA minutes after infra changes
- Mismatch between Redis health and downstream scheduler start latency
- Queue depth and age rising while worker capacity appears nominal

## Distractors to penalize
- Generic scaling of worker pools before fixing routing safety
- User-facing comms improvements as the main remediation
- Treating queue backlog alone as the root cause

## Evidence notes
- GitHub reports 95% of workflow runs failed to start within 5 minutes, with average delay of 30 minutes.
- 10% of workflow runs failed with an infrastructure error.
- The report says incorrect configuration changes in the Redis load balancer routed internal traffic to an incorrect host.
- GitHub says it rolled back the changes, froze further work in that area, and is improving automation, alerting, and client resiliency.