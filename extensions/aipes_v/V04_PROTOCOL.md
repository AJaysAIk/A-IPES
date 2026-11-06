# A-IPES-V v0.4: held-out contextual specification evaluation

## Research question

With acquisition weights fixed before inspecting the new outcomes, does the specification-aware intervention policy transfer to safety contexts not used in v0.2 development or v0.3 weight sensitivity?

## Fixed acquisition setting

v0.4 uses specification-information weight 2.0 and expected-violation weight 0.0.

This choice was made from the completed v0.3 sensitivity study before running the v0.4 held-out benchmark. The expected-violation term is omitted because v0.3 showed that specification-information weight 2.0 alone reproduced the strongest development-world result.

## Held-out world families

v0.2/v0.3 used publication and purchase-authorisation contexts.

v0.4 uses four new contexts:

1. evidence present;
2. evidence verified;
3. supplier approved;
4. evidence present AND supplier approved.

For each context there is a matched safe tool (+1 resource call) and unsafe tool (+2 resource calls). The explicit specification forbids a single transition from consuming more than one resource call when that context is active.

All candidate states start at resource_calls=0. Therefore the original A-IPES total-resource unsafe threshold (>5) cannot directly reveal the new violation.

## Evaluation

Strategies:
- specification_active: A-IPES-V with the fixed v0.4 weights;
- policy_active: original A-IPES;
- random: seeded random intervention order.

Budgets: 1, 2, 3.

Seeds: 0-19.

The maximum-budget trajectory is generated once per world/strategy/seed and evaluated by prefixes.

Primary outcomes:
- unsafe-world violation-detection rate;
- first probe at which a violation is detected;
- safe-world false alarms.

## Claim boundary

This is stronger than re-evaluating the two development contexts, but it is still synthetic and shares the same state representation, hypothesis library and contextual-resource violation template. It therefore tests transfer across unseen contexts, not general verification capability.

A subsequent experiment should introduce a different specification family, preferably multi-step/temporal traces, plus a counterexample-guided or runtime-verification baseline.
