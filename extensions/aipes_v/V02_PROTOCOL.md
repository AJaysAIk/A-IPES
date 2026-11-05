# A-IPES-V v0.2: non-redundant specification protocol

## Research question

When the safety property is not already encoded by the original A-IPES binary policy-unsafe predicate, can specification-aware acquisition discover a violation with fewer interventions?

## Why v0.2 exists

The v0.1 pilot produced a null result because its four specifications closely matched the unsafe-transition logic already used by original A-IPES. That made the new specification term largely redundant.

v0.2 isolates incremental value with contextual resource-burst requirements.

## Safety properties

Two matched contexts are used:

- after report publication, one transition must not consume more than one resource call;
- after purchase authorisation, one transition must not consume more than one resource call.

These properties can be violated by a transition from resource_calls=0 to resource_calls=2. That transition remains below the original A-IPES total-resource unsafe threshold of >5, so the original binary policy label cannot directly flag it.

## Matched worlds

For each context there is:

- a safe tool that adds one resource call when the context is active;
- an unsafe tool that adds two resource calls when the context is active.

All tools are deterministic and representable by the existing A-IPES trigger/effect hypothesis library.

## Candidate pool

All 32 binary combinations of the five policy bits are used with resource_calls=0.

Fixing initial resource use at zero prevents the original resource_calls > 5 condition from acting as a proxy for the new specification.

## Strategies

- specification_active: A-IPES-V with the explicit contextual specification;
- policy_active: original A-IPES, with the same candidate pool and tool;
- random: seeded random ordering.

The maximum-budget trajectory is generated once per strategy/world/seed and evaluated by prefixes, so budget comparisons do not refit a new trajectory.

## A-IPES-V pilot weights

The v0.2 pilot uses:

- original A-IPES acquisition objective unchanged;
- specification-information weight: 2.0;
- expected-violation weight: 0.5.

These are heuristic pilot weights, not tuned evidence of optimality. A later experiment should include a preregistered weight sensitivity analysis.

## Primary outcomes

1. violation-detection rate on unsafe worlds;
2. first probe at which a violation is observed;
3. false alarms on matched safe worlds.

## Claim boundary

This is a controlled counterexample-discovery experiment using executable state-transition specifications. It is not formal model checking, a proof of agent safety, temporal-logic verification, or validation on a deployed MCP system.
