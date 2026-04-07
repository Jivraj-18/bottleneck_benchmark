# GitHub multi-service degradation from user-settings cache rewrite cascade — Gold packet

## Binding Constraint Top1

A user-settings cache configuration change that triggered high-volume cache rewrites, overwhelming shared coordination/proxy infrastructure and exhausting Git HTTPS proxy connections.

## Binding Constraint Top3

- Write amplification in a shared caching mechanism tied to many services
- Lack of self-throttling / rollback responsiveness in bulk cache updates
- Proxy layer inability to self-recover from connection exhaustion

## Slow Variables

- Caching architecture and write-amplification behavior
- Isolation of shared infrastructure components from bulk background work
- Rollback and throttling safeguards for cache/config changes
- Recovery behavior of the Git HTTPS proxy layer

## Contributing Factors

- The first incident came from asynchronous rewrites overwhelming a shared infrastructure component.
- The second incident came from an additional synchronous write source that bypassed the initial mitigation.
- Shared components caused the blast radius to include github.com, API, Actions, Copilot, webhooks, Pages, Codespaces, and more.

## Good Interventions Ranked

- Redesign the caching mechanism to reduce write amplification and add self-throttling during bulk updates.
- Strengthen rollout/validation/rollback safeguards for caching-system configuration changes.
- Fix the Git HTTPS proxy failure mode so connection exhaustion does not require manual restarts to recover.

## Bad Interventions

- Front-end performance work
- Scaling only one affected service such as Actions without fixing the shared cache/proxy cascade
- Treating each impacted product separately instead of as a shared-systems issue

## Early Warning Signals

- Sharp increase in cache rewrite volume during/after config changes
- Shared coordination infrastructure saturation
- Git HTTPS proxy connection pool exhaustion while SSH Git remains healthy

## Distractors To Penalize

- Purely product-specific mitigations
- Extra capacity alone without write-amplification control
- General customer support improvements

## Evidence

- The status report says both incidents shared the same underlying cause: a configuration change to the user settings caching mechanism.
- Immediate steps focused on reducing write amplification, adding self-throttling, hardening rollbacks, and fixing proxy recovery.
