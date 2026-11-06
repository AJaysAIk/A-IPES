# v0.6 results: a consistent model can still be inadequate

## Frozen design and evidence
Protocol commit `5d3bb99` was pushed before the v0.6 outcomes were run. No worlds,
weights, horizons, seeds, acquisition rules or call budgets were retuned after
outcomes. Adding the aggregate CSV is a reporting change only.

Reproduce from the repository root:

```sh
python extensions/aipes_v/scripts/run_misspecification.py --output-dir /tmp/v06
```

Evidence under `results/v06/`: `rows.csv` (3,840 budget-prefix records),
`traces.jsonl` (7,680 full query audits), `oracle.json` (all 12 worlds checked over
4,096 traces each), and `summary.csv` (aggregate counts and logical work totals).
Every query executes six actions; budgets 1/2/4/8 therefore cost 6/12/24/48 action
calls. Resets are recorded separately. Twenty seeds vary the paired candidate
order and the CEG model order; they are not independent world samples.

The existing eight hypotheses have no expiry mechanism. The exhaustive oracle
confirms ten worlds are out of class and two are realizable by that library.
There are four safe worlds and eight unsafe worlds under the lease-age-2 monitor.
Out-of-class status is determined by response equivalence on this finite pool,
not an unbounded equivalence proof.

## Observed violation detection (numerator / 160 unsafe world-seed cases)

| Strategy | 1 trace | 2 traces | 4 traces | 8 traces |
|---|---:|---:|---:|---:|
| specification_active | 50 | 54 | 60 | 90 |
| transition_active | 50 | 54 | 60 | 90 |
| counterexample_guided | 44 | 83 | 110 | 122 |
| random | 26 | 34 | 56 | 80 |

Specification weighting adds no detection benefit here. CEG has lower aggregate
first-query detection than both information methods, but higher detection at
budgets 2, 4 and 8. This is a within-benchmark observation, not general superiority.

## Detected model inadequacy (numerator / 200 out-of-class world-seed cases)

| Strategy | 1 trace | 2 traces | 4 traces | 8 traces |
|---|---:|---:|---:|---:|
| specification_active | 0 | 14 | 34 | 92 |
| transition_active | 0 | 14 | 34 | 92 |
| counterexample_guided | 48 | 112 | 166 | 178 |
| random | 14 | 18 | 50 | 88 |

All strategies have zero false mismatch flags on the 40 in-class world-seed cases
at each budget. However, even CEG leaves 22/200 out-of-class cases unflagged by
48 calls; the information methods leave 108/200 unflagged. Nonempty posteriors
therefore cannot be interpreted as evidence of adequacy.

## Outcomes by world kind at eight traces (each denominator 40)

Entries are observed safety violations / detected model mismatches.

| World kind | Specification | Transition | CEG | Random |
|---|---:|---:|---:|---:|
| compliant expiry | 0 / 14 | 0 / 14 | 0 / 40 | 0 / 14 |
| premature expiry | 0 / 30 | 0 / 30 | 0 / 40 | 0 / 32 |
| late expiry | 14 / 6 | 14 / 6 | 30 / 39 | 14 / 6 |
| ignores expiry | 14 / 0 | 14 / 0 | 40 / 0 | 14 / 0 |
| early use | 40 / 14 | 40 / 14 | 38 / 19 | 38 / 14 |
| stale authority | 22 / 28 | 22 / 28 | 14 / 40 | 14 / 22 |

Safety and model adequacy are distinct. The in-class ignores-expiry tool violates
the specification despite being represented by the model library. Safe compliant
and premature-expiry tools can refute every model without violating the safety
property. The CEG baseline detects every stale-world mismatch by budget 4 yet
observes only 14/40 stale-world safety violations by budget 8. Discovering an
inadequate model does not itself discover the defect, and the prescribed uniform
exploration after posterior collapse provides no further model-based guidance.

Safe-world violation alarms are 0/80 for every strategy/budget. At budget 8,
safe-world mismatch counts are 44/80 for each information method, 80/80 for CEG,
and 46/80 for random. These mismatch flags must not be reported as safety alarms.

## Search work and censoring
`summary.csv` includes cumulative logical selection and refinement lookup totals.
For all 240 world-seed trajectories at budget 8, CEG performs 29,631 candidate
checks, versus 6,712,528 for each information method and 1,920 for random. CEG
checks may revisit a candidate for different models. The information methods each
require 13,593,528 logical response lookups; specification-active additionally
requires the same number of violation-label lookups. CEG records 28,625 such
violation lookups. These are logical counts excluding prediction precomputation,
score-cache construction/reuse, and oracle evaluation; they are not CPU timings
or a compute-normalized performance comparison. The implementation caches scores.

Undetected first-violation and first-mismatch values stay empty. Detection is
incomplete even at the largest budget, so detected-only mean timings should not
be compared as though all cases detected. Every actual trace, response, posterior
size and first-event cost can be checked in the saved evidence.

## Supported conclusion and next question
On this fixed bounded lease benchmark, posterior collapse provides an explicit
model-inadequacy signal for some safe and unsafe tools. It is incomplete under
finite call budgets. Specification entropy again provides no incremental
violation-detection advantage over response entropy. CEG finds more mismatches
and more violations at larger budgets overall, while missing some defect types
that the information methods detect more often.

The next defensible experiment would preregister a recovery policy after model
collapse, such as expanding the model class with lease clocks, and compare it
with continued uniform exploration at equal action-call budgets. That experiment
has not been performed here. This study establishes neither general OOD detection
nor unbounded verification, real-agent safety, or novelty over existing methods.
