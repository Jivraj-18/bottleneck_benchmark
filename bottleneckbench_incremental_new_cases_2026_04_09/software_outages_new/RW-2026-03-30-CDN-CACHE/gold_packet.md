# Gold packet — RW-2026-03-30-CDN-CACHE

## Binding constraint (top 1)
Configuration safety around shared-cache enablement for domains that were supposed to be uncached — specifically, the lack of a hard, testable guardrail that prevents infrastructure changes from turning opt-in caching into implicit shared caching.

## Acceptable top-3 near-equivalents
- Unsafe cache-boundary enforcement between CDN-enabled and CDN-disabled domains
- Rollout safety and pre-production validation for CDN behavior changes
- Reliance on application-origin cache headers where the platform contract itself should have enforced no-cache behavior

## Slow variables
- Platform configuration hygiene and invariants around cache eligibility
- Test coverage for negative caching cases and auth-sensitive responses
- Rollout discipline and shard size for edge/platform changes
- Safety-vs-speed engineering culture during rapid growth

## Contributing factors
- A surrogate-key update accidentally enabled caching on domains where it should have been disabled
- Most GET responses without explicit cache headers were cached by default during the incident window
- Detection relied partly on user reports rather than a hard pre-release block
- The product contract ('CDN disabled') was not enforced as a non-bypassable control

## Good interventions (ranked)
1. Enforce a hard platform invariant that CDN-disabled domains can never enter shared-cache paths, regardless of provider configuration.
2. Add pre-production and canary tests that explicitly verify wrong-user / auth-sensitive responses cannot be cached on uncached domains.
3. Slow and shard CDN/infrastructure rollouts with automatic rollback on anomalous cache-hit behavior or cross-domain cache activation.

## Bad / deprioritized interventions
- Generic incident communication improvements without changing cache invariants
- Telling customers to set better cache headers as the primary fix
- Focusing mainly on faster purge tooling while leaving cache enablement guardrails weak

## Early-warning signals
- Unexpected cache-hit activity on domains marked CDN-disabled
- Any increase in cacheable GET responses from auth-protected routes during rollout canaries
- User/session mismatch anomalies or sudden spikes in cross-user content complaints
- Configuration diffs that widen cache eligibility scope

## Distractors to penalize
- More dashboards without policy enforcement
- Customer education as the main fix
- Broad calls for 'better security culture' without specific cache-boundary controls

## Evidence notes
- The report says CDN features were accidentally enabled for some domains without users enabling them.
- The impact window ran from 10:42 UTC to 11:34 UTC and affected ~0.05% of domains with CDN disabled.
- Responses, including authenticated ones without Set-Cookie, were stored and served from edge cache.
- Railway says most GET responses without explicit cache headers were cached by default during the window.
- The stated preventions were more tests and slower sharded rollouts.