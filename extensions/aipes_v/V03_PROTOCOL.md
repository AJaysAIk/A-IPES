# A-IPES-V v0.3: acquisition-weight sensitivity

## Purpose

Test whether the v0.2 counterexample-discovery result depends narrowly on the heuristic specification-information (2.0) and expected-violation (0.5) weights.

## Design

Keep the exact four v0.2 worlds, candidate pool, baseline acquisition and matched seeds fixed. Sweep six **predeclared** specification-weight pairs: (0,0), (0.5,0), (1,0), (2,0), (2,0.5), (4,1). Evaluate budgets 1 and 2, report unsafe detection and safe-world false alarms. Zero specification weights should reproduce the original policy-active selector.

The weights are diagnostic and were chosen after seeing v0.2 results. This is **not** a preregistered or held-out validation, and cannot establish generality.

## Interpretation rules

- Report every weight pair, including ties and failures.
- Treat repeated seeds over only two deterministic unsafe worlds as correlated observations, not 20 independent tasks.
- Do not claim statistical significance from the seed count alone.
- Follow with held-out world families, temporal traces and a genuine counterexample-guided baseline before a general claim.
