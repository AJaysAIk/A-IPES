# Benchmark V2: Independent Benchmark Replicates

Benchmark V2 changes the statistical unit from repeated execution on one fixed
world to independently generated benchmark worlds.

Each `benchmark_seed` deterministically changes:

- conditional approval, purchase, and publication triggers;
- resource thresholds and effect magnitudes;
- deceptive alias names and descriptions;
- catalogue ordering.

Every strategy receives the same generated world for a given seed, enabling
paired comparisons. `probe_seed` is separate and controls within-strategy tie
breaking or random probing only.

The primary analysis compares A-IPES (`policy_active`) against
`passive_characterisation` using paired bootstrap confidence intervals and a
paired sign-flip randomisation test over benchmark replicates.

Final posterior counts are not compared in isolation because passive metadata
priors may start with fewer hypotheses. Benchmark V2 therefore reports initial
and final hypothesis counts, posterior reduction ratio, and information gain.
