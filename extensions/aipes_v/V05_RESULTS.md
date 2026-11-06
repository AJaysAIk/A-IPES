# v0.5 measured results: a null incremental acquisition result

## Provenance
Protocol frozen and pushed in commit `64f9787` before outcomes were generated.
No acquisition parameters, worlds, seeds, or budget changes were made after seeing
results. The implementation is in `src/aipes_v/temporal.py`; reproduce from the
repository root with:

```sh
python extensions/aipes_v/scripts/run_temporal_demo.py --output-dir /tmp/v05
```

Evidence: `results/v05/rows.csv` (2,560 rows) and `results/v05/traces.jsonl`
(5,120 audited queries). Each of eight worlds has 20 seeds, four strategies,
four reported budgets, and eight executed trace queries per trajectory. These
are repeated measurements of eight deterministic models, not independent worlds.
The dedicated temporal CI regenerates and byte-compares both evidence files on
Python 3.11 and 3.12; consult its actual status before claiming CI reproduction.

## Unsafe detection (numerator / 120 world-seed cases)

| Strategy | 1 trace / 4 calls | 2 traces / 8 calls | 4 traces / 16 calls | 8 traces / 32 calls |
|---|---:|---:|---:|---:|
| specification_active | 80/120 | 120/120 | 120/120 | 120/120 |
| transition_active | 80/120 | 120/120 | 120/120 | 120/120 |
| counterexample_guided | 84/120 | 120/120 | 120/120 | 120/120 |
| random | 44/120 | 68/120 | 70/120 | 92/120 |

Each trace executes four actions even when the first violation occurs earlier.
Resets are recorded separately and excluded from action-call cost as preregistered.
All strategies have 0/40 safe-control alarms at each budget (0/640 across all
repeated strategy/budget rows).

## Mutant-level first-trace detection (numerator / 40)

| Strategy | Early use | Stale approval after revoke | Both defects |
|---|---:|---:|---:|
| specification_active | 40/40 | 0/40 | 40/40 |
| transition_active | 40/40 | 0/40 | 40/40 |
| counterexample_guided | 4/40 | 40/40 | 40/40 |
| random | 20/40 | 2/40 | 22/40 |

The fixed model enumeration makes CEG consider a stale-approval model first.
Its first-trace advantage is therefore ordering-dependent, not evidence of
universal superiority. The two information strategies have identical detection
outcomes here; this does not imply every selected trace is identical.

Undetected cases retain empty first-detection fields. For the information methods,
80 unsafe cases first detect at query 1 and 40 at query 2; for CEG, these counts
are 84 and 36. Averaged across all 120 unsafe cases, first detection costs are
5.333 and 5.2 calls respectively. For random, only 92/120 detect by 32 calls;
a detected-only mean would be censored and should not be compared as though all
cases detected. Raw per-case timing remains available for audit.

## Interpretation
The temporal adapter can discover concrete history-dependent safety violations
and refine from observed traces. **This experiment does not show incremental
value from specification entropy over response entropy.** CEG matches full
coverage by query 2 and has slightly better aggregate first-query coverage in
this setup. This is a useful null result, not support for an A-IPES-V superiority
claim. No post-outcome tuning was performed.

The class is tiny, deterministic, realizable, and fully known to every adaptive
strategy. Only one authorization/revocation property and length-four traces are
tested. A useful next protocol would test model misspecification and longer
histories with a fixed compute/call budget and randomized CEG model ordering;
those are proposed future experiments, not measured findings here.

## Completed CI reproduction

At implementation commit `1fbfefbfb6ab7735c3ca2bcb45bbf8c00fb0659d`,
[Actions run 42248704961](https://github.com/AJaysAIk/A-IPES/actions/runs/42248704961)
passed on both Python 3.11 and 3.12: lint, nine temporal tests, the full frozen
benchmark, byte comparison of every saved row and query audit, and artifact
upload. This verifies reproducibility of v0.5 evidence on those two environments.
The broader extension workflow has a separate status and is not implied by this
statement. The complete 32-test extension suite also passed locally.
