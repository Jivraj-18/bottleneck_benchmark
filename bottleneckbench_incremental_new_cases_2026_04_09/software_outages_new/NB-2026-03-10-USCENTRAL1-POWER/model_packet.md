# NB-2026-03-10-USCENTRAL1-POWER — Nebius us-central1 provider-maintenance power incident

## Background
A cloud provider suffered a major regional outage during scheduled provider-led electrical maintenance. The customer impact spread across networking, storage, Kubernetes, and shared control-plane services, and the incident involved repeated interruptions while recovery was already underway.

## System context
- The maintenance had been planned around a narrower and more controlled expected impact.
- Customer-facing networking, storage, Kubernetes, and control functions share regional dependencies.
- Power returned to different parts of the site at different times.
- Some services required manual intervention during restoration.

## Timeline
- 2026-03-10 15:18 UTC: unexpected power event affects multiple racks during provider-led electrical maintenance.
- 2026-03-10 15:24 UTC: incident is declared.
- 2026-03-10 17:04 UTC: broad external VM connectivity impact begins to ease.
- 2026-03-10 19:53 UTC, 20:54 UTC, 22:37 UTC: later interruptions affect recovering services.
- 2026-03-11 00:50 UTC: customer impact fully mitigated.

## Observations
- External VM connectivity, public S3 endpoints, Kubernetes clusters, and control-plane workloads were all affected.
- The report emphasizes that repeated outages interacted badly with platform architecture.
- Recovery was prolonged not just by the initial outage but by how restoration was organized.
- This is a region-level dependency and incident-command problem as much as a hardware event.

## Task
Analyze this case. Identify the main binding constraint, the slow variables, the top 3 interventions, 2 things to deprioritize, and the earliest warning signals leadership should track.