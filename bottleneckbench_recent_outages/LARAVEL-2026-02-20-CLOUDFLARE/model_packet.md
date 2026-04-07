# Laravel Cloud connectivity outage from upstream BYOIP dependency — Model packet

## Background

A cloud application platform experienced a connectivity outage lasting about 3 hours and 15 minutes. Customer apps, the control panel, and API became unreachable. Running apps, databases, and caches remained healthy, and no customer data was lost.

## System Context

- The platform relies on an upstream network provider for BYOIP-style IP prefix management.
- The outage was network-level: applications and infrastructure kept running but could not be reached.
- The team has redundancy in much of its infrastructure, but not yet in the IP announcement layer.

## Timeline

- 18:42 UTC: platform monitoring detected connectivity failures; incident declared.
- 18:45 UTC: upstream provider began investigating network issues.
- 18:48 UTC: status page and social notification updated.
- 19:09 UTC: upstream provider identified impact to a subset of BYOIP prefixes and said the underlying issue was mitigated; restoration work began.
- Around 19:40 UTC: platform attempted to re-advertise prefixes through the provider dashboard, but the prefixes were locked in a withdrawn state.
- 20:50 UTC: upstream provider acknowledged some customers could not re-advertise through the dashboard and began working on a fix.
- 21:57 UTC: full connectivity restored.

## Observations

- The team's monitoring caught the issue before the upstream status page reflected it.
- A suggested self-mitigation path existed in theory but was unavailable in practice because prefixes were locked.
- Recovery depended on the upstream provider unlocking or restoring the prefixes.
- The platform explicitly said a single upstream dependency could still cause prolonged outage.

## Task

Identify the binding constraint and slow variables. What truly governed outage duration here? Recommend the top 3 interventions and 2 things to deprioritize.
