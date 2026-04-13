# Gold packet — NB-2026-02-26-EUNORTH1-RESTART

## Binding constraint (top 1)
Cross-layer recovery throughput under region-level mass restarts — especially compute control-plane capacity and storage-state reconciliation after simultaneous host reboot events.

## Acceptable top-3 near-equivalents
- Insufficient compute control-plane recovery throughput for mass VM restarts
- Storage attachment state inconsistencies after host reboots
- Lack of region-level restart readiness across power, compute, and storage layers

## Slow variables
- Compute control-plane throughput and restart behavior under mass failure conditions
- Storage state persistence and reconciliation logic after host reboot
- Cross-layer observability spanning power, compute, and storage during restart events
- Electrical protection selectivity and configuration at the facility layer

## Contributing factors
- A short circuit in cooling-infrastructure cabling triggered UPS protection and a brief power interruption
- Affected compute hosts restarted simultaneously
- Recovery throughput was slower than expected under mass-restart conditions
- Storage attachment conflicts prevented some VMs from starting or regaining disk access cleanly

## Good interventions (ranked)
1. Increase compute control-plane recovery throughput and validate restart behavior under region-level mass-restart scenarios.
2. Fix storage attachment state handling and reconciliation after host reboots to avoid stale attachment conflicts.
3. Add cross-layer monitoring and drills for region-level restart scenarios spanning power, compute, and storage.

## Bad / deprioritized interventions
- Focusing only on the initiating electrical fault while ignoring restart behavior
- Customer-communication-only remediation
- Generic capacity additions that do not address mass-restart recovery paths

## Early-warning signals
- Recovery throughput dropping below expected VM-restart rates during bulk events
- Storage attach / detach conflict rates increasing after host reboot storms
- Large gaps between host power return and workload restoration
- Cross-layer alerting that shows compute recovery lagging despite electrical stability

## Distractors to penalize
- Treating the incident purely as a datacenter power-quality problem
- Dashboard/UI improvements
- Generic redundancy talk without mass-restart recovery fixes

## Evidence notes
- Nebius says the initial interruption was brief but recovery constraints in compute and storage extended time to full restoration.
- The report names throughput limitations in compute control-plane recovery operations during mass VM restarts.
- It also names storage attachment state inconsistencies after host reboots as a contributing factor.
- The action plan includes improving compute recovery throughput, refining storage state handling, and enhancing cross-layer monitoring.