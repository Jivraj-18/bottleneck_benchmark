# Gold packet — NB-2026-03-10-USCENTRAL1-POWER

## Binding constraint (top 1)
Readiness for region-level dependency-ordered recovery under broader-than-planned power events — including provider risk assumptions, blast-radius planning, and restoration sequencing for shared control-plane dependencies.

## Acceptable top-3 near-equivalents
- Insufficient preparation for a wider power-maintenance blast radius plus repeated interruptions
- Lack of a strict dependency-ordered regional recovery algorithm
- Shared regional control-plane and networking dependencies that did not recover automatically after staggered power return

## Slow variables
- Maintenance governance and joint planning quality with the facility provider
- Regional architecture and auto-recovery behavior for shared control-plane workloads
- Runbook maturity for region-level recovery sequencing
- Operational discipline around stop-and-review criteria during unstable maintenance

## Contributing factors
- Provider-led work expanded beyond the announced maintenance profile
- Unexpected power failures affected additional racks serving networking and shared control-plane services
- Later interruptions happened while recovery was already underway
- Too much recovery was handled as parallel service-by-service restoration instead of a stricter dependency-ordered regional sequence

## Good interventions (ranked)
1. Adopt dependency-ordered regional recovery playbooks and drills for large-scale power incidents, rather than relying on parallel service-by-service restoration.
2. Strengthen provider maintenance governance with wider blast-radius assumptions, explicit stop-and-review triggers, and higher planning-quality thresholds.
3. Harden and test auto-recovery of shared networking/control-plane services when power returns unevenly across the region.

## Bad / deprioritized interventions
- Only improving customer status messaging without changing maintenance and recovery practices
- Treating the incident as just a single hardware anomaly
- Adding more service-specific dashboards without region-level restoration logic

## Early-warning signals
- Maintenance changes whose assumed blast radius excludes shared control-plane or networking racks
- Recovery progression where hosts come back before dependent control services are healthy
- Repeated power interruptions during an active restoration window
- Manual reconciliation counts rising for gateways, control-plane components, or storage-backed workloads

## Distractors to penalize
- General calls for more redundancy without addressing recovery sequencing
- Purely service-local fixes
- Comms-only remediations

## Evidence notes
- Nebius says maintenance had been planned around a much narrower expected impact, but unexpected power failures hit additional racks serving networking and shared control-plane services.
- The report states some networking gateways, control-plane components, and storage-backed workloads did not recover automatically.
- Nebius explicitly says too much recovery was handled as parallel service-by-service restoration instead of a stricter dependency-ordered regional sequence.
- The action plan includes wider blast-radius assumptions, stop-and-review criteria, and regional recovery drills.