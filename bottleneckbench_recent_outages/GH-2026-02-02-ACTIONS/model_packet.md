# GitHub Actions outage from provider policy change blocking VM metadata — Model packet

## Background

A large code-hosting platform had a major incident in which hosted CI runners became unavailable across all regions and all runner types. Jobs queued and timed out waiting for hosted runners. Several dependent features were also affected, while self-hosted runners on other providers were not.

## System Context

- The affected service depends on compute-provider primitives for VM lifecycle operations.
- Impacted features included Actions and several features that rely on the same compute infrastructure.
- Self-hosted runners outside the affected provider were not impacted.

## Timeline

- 18:35 UTC: hosted runners became unavailable.
- 19:03 UTC: public incident opened for Actions.
- 21:13 UTC: team said root cause was identified and they were working with the upstream provider.
- 22:53 UTC: upstream provider applied mitigation; telemetry improved.
- 23:50 UTC: most customers should see recovery from failing hosted-runner jobs.
- Full recovery occurred later for standard and larger runners after backlog drained.

## Observations

- Impact spanned all regions and runner types, which is atypical for this area.
- The outage blocked VM create, delete, reimage, and related operations.
- The root issue originated in the underlying compute provider rather than GitHub application logic.
- Recovery required upstream rollback before queues could drain.

## Task

Identify the binding constraint and slow variables. What governed global impact here, and what are the top 3 interventions and 2 deprioritized actions?
