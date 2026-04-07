# Clerk outage from failed Cloud SQL live migration — Model packet

## Background

An authentication platform saw increased latency, elevated 5xx errors, and widespread request throttling. Session management was partially restored during the incident via an outage mode, but many requests still returned errors. The incident resolved on its own after roughly 26 minutes.

## System Context

- The platform depends on a managed PostgreSQL offering with high availability.
- The database CPU remained within normal limits during the incident.
- Monitoring showed increased lock contention and elevated read-side IO wait without a corresponding increase in writes.
- Attempts to offload reads to replicas did not help.

## Timeline

- 15:57 UTC: alerting detected increased latency and elevated 5xx errors; lock contention had started about a minute earlier.
- During investigation: no clear smoking gun; team attempted to move reads to replicas, without success.
- Compute resources became saturated as queries and transactions slowed, leading to 429 responses.
- Session outage resiliency triggered automatically but most session token requests still returned 429 while compute remained saturated.
- 16:10 UTC: team enabled Origin Outage Mode, restoring session operations.
- During investigation: team noted unusual elevated IO wait on reads without matching write increase and suspected an infrastructure issue.
- 16:23 UTC: issue resolved on its own; platform stabilized.

## Observations

- The database itself looked 'up' and CPU was normal, making the issue harder to diagnose from usual signals.
- The failure mode had been seen before in a related form months earlier.
- The service relies on maintenance behaviors of a managed database provider and does not get advance notice of certain operations.
- The company later said it may need to migrate providers or operate the database itself if this behavior cannot be disabled.

## Task

Identify the binding constraint and slow variables. What governed outage severity and repeatability here? Recommend the top 3 interventions and 2 things to deprioritize.
