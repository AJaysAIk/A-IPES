# A-IPES-V v0.3: acquisition-weight sensitivity results

## Scope

This study reuses the v0.2 non-redundant worlds, candidate pool and matched seeds. It varies only the two added A-IPES-V acquisition weights. Because the same worlds were already used to design v0.2, this is a robustness diagnostic, not held-out validation.

The six predeclared weight pairs were:

- (0.0, 0.0)
- (0.5, 0.0)
- (1.0, 0.0)
- (2.0, 0.0)
- (2.0, 0.5)
- (4.0, 1.0)

The first value is the specification-information weight and the second is the expected-violation weight.

## Results

Unsafe-world detection rates:

| Strategy / weights | Budget 1 | Budget 2 | Mean first probe when detected |
|---|---:|---:|---:|
| original policy_active | 0.00 | 0.50 | 2.00 at B2 |
| A-IPES-V (0.0, 0.0) | 0.00 | 0.50 | 2.00 at B2 |
| A-IPES-V (0.5, 0.0) | 0.00 | 1.00 | 2.00 |
| A-IPES-V (1.0, 0.0) | 0.00 | 1.00 | 2.00 |
| A-IPES-V (2.0, 0.0) | 1.00 | 1.00 | 1.00 |
| A-IPES-V (2.0, 0.5) | 1.00 | 1.00 | 1.00 |
| A-IPES-V (4.0, 1.0) | 1.00 | 1.00 | 1.00 |

All matched safe-world false-alarm rates were 0.00 for every configuration and both budgets.

Zero specification weights reproduce original A-IPES exactly on the reported outcomes, which is an internal consistency check.

## Interpretation

The v0.2 result is not tied to the single (2.0, 0.5) setting: removing the expected-violation term while retaining specification-information weight 2.0 still gives 100% detection at probe 1 in this pilot.

However, performance is clearly weight-sensitive under the tightest budget. Specification-information weights 0.5 and 1.0 do not improve budget-1 detection, although they improve budget-2 detection from 50% to 100%.

Therefore the evidence supports a narrower claim: in these controlled non-redundant worlds, sufficiently strong specification-information weighting changes intervention priority and can expose the counterexample earlier. It does not show that arbitrary or weak specification weighting is beneficial.

## Validation

GitHub Actions completed successfully on Python 3.11 and 3.12. Ruff, the extension test suite, the v0.1 demo, v0.2 pilot and v0.3 sensitivity runner all passed.

## Next experiment

The next experiment must move away from the two development specification families. Use held-out specification/world families, fixed weights selected before examining those results, and report every failure. A stronger next step also adds multi-step/temporal properties and a genuine counterexample-guided baseline.
