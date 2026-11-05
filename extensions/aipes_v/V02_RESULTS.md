# A-IPES-V v0.2 pilot results

## Scope

This result comes from the controlled non-redundant specification pilot defined in V02_PROTOCOL.md. It uses two unsafe contextual-resource worlds and two matched safe controls, ten paired seeds, and intervention budgets 1 and 2.

The new safety properties are intentionally outside the original A-IPES binary policy-unsafe predicate: after publication or purchase authorisation, a single transition must not consume more than one resource call. Candidate states start at resource_calls=0, so the original total-resource threshold (>5) cannot act as a proxy.

## Results

Across the two unsafe worlds and ten seeds, there are 20 unsafe evaluations per strategy at each budget.

| Strategy | Budget | Unsafe detections | Detection rate | Mean first violation probe when detected |
|---|---:|---:|---:|---:|
| specification_active (A-IPES-V) | 1 | 20/20 | 1.00 | 1.00 |
| policy_active (original A-IPES) | 1 | 0/20 | 0.00 | n/a |
| random | 1 | 10/20 | 0.50 | 1.00 |
| specification_active (A-IPES-V) | 2 | 20/20 | 1.00 | 1.00 |
| policy_active (original A-IPES) | 2 | 10/20 | 0.50 | 2.00 |
| random | 2 | 16/20 | 0.80 | 1.375 |

Across all matched safe-world rows in this CI sweep, the runtime monitors produced 0/120 false alarms.

## Validation

GitHub Actions ran the extension on Python 3.11 and 3.12.

- Ruff: passed.
- Extension test suite: 15 passed.
- Original v0.1 demo: passed.
- v0.2 non-redundant demo: passed on both Python versions.

The recorded CI command was:

    python extensions/aipes_v/scripts/run_nonredundant_demo.py --budgets 1,2 --seeds 0,1,2,3,4,5,6,7,8,9

## Interpretation

Within this deliberately small synthetic benchmark, explicit specification information changes the intervention selected under a tight budget. At budget 1, A-IPES-V targets the context in which the known safety property can be violated, while original A-IPES optimises its broader policy-identification objective and misses both contextual burst violations.

This is evidence of incremental value for **counterexample discovery under a known, non-redundant runtime specification** in this controlled state model.

It is not evidence that A-IPES-V is generally superior to A-IPES. The benchmark was designed after the v0.1 null result specifically to isolate a case where the new specification objective has information unavailable to the original binary policy label.

## Limitations and next tests

The current evidence is still pilot-scale and synthetic. Before making a stronger research claim, the next evaluation should include:

1. more independent specification families and tool behaviours;
2. predeclared acquisition-weight sensitivity rather than a single heuristic setting;
3. larger held-out world generation;
4. statistical paired analysis across worlds;
5. multi-step or temporal specifications;
6. comparison with counterexample-guided/runtime-verification baselines;
7. real MCP or tool-agent traces.

No formal verification, model-checking guarantee, deployed-agent safety guarantee, or generalisation claim is made.
