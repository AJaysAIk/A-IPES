# v0.4 verified held-out findings

Reviewed PR #5 head: `0310bbc8dcf5a7ef17d4c79e4787c8e67f673490`.
CI: https://github.com/AJaysAIk/A-IPES/actions/runs/42245880884

Both Python 3.11 and 3.12 passed Ruff, 23 extension tests, and all benchmark
steps. Their held-out summaries agree. PR #5 was merged after these checks, as
merge commit `a607c0e58bd806a87da57745d3d9b3b1817f4d66`.

## Logged unsafe detection rates

Each entry is the CI-printed rate, rounded to three decimal places, over four
unsafe worlds and 20 seeds (80 world-seed cases per strategy/budget).

| Strategy | Budget 1 | Budget 2 | Budget 3 |
|---|---:|---:|---:|
| specification_active | 0.750 | 1.000 | 1.000 |
| policy_active | 0.000 | 0.250 | 0.613 |
| random | 0.388 | 0.650 | 0.825 |

Mean first violation probe **conditional on detection**:

| Strategy | Budget 1 | Budget 2 | Budget 3 |
|---|---:|---:|---:|
| specification_active | 1.000 | 1.250 | 1.250 |
| policy_active | undefined | 2.000 | 2.592 |
| random | 1.000 | 1.404 | 1.742 |

Because detection rates differ, these conditional means should not be interpreted
as uncensored comparisons of expected time to detection.

Safe-control alarms were 0/720 repeated rows across four safe worlds, 20 seeds,
three strategies and three budget prefixes. These are neither 720 distinct
worlds nor independent trials. The two Python runs are reproducibility checks,
not additional statistical samples.

## Interpretation
Fixed v0.3 weights transfer to unseen contexts **within the same synthetic
contextual-resource template**. First-probe transfer is incomplete (75%, versus
100% in the development benchmark), while detection reaches 100% by budget 2 in
this finite evaluation. We do not infer general verification capability, formal
proof, out-of-class robustness, or deployed-agent safety.

The original protocol says weights were fixed before inspecting v0.4 outcomes;
that is the repository's protocol history, not an independently auditable claim
about all possible prior human access. No retuning was done in this continuation.

## Local raw-row reproduction

The unmodified v0.4 runner was also rerun locally with its default frozen budgets
and seeds, saving all 1,440 rows to `results/v04/rows.csv`. Every printed summary
matches both CI logs above. Exact unsafe detection numerators (denominator 80):

| Strategy | Budget 1 | Budget 2 | Budget 3 |
|---|---:|---:|---:|
| specification_active | 60 | 80 | 80 |
| policy_active | 0 | 20 | 49 |
| random | 31 | 52 | 66 |

The first-probe shortfall is concentrated entirely in the conjunction context:
evidence present, evidence verified, and supplier approved each detect 20/20;
evidence-present AND supplier-approved detects 0/20. All four contexts detect
20/20 by budget 2. This is a concrete limitation of first-probe transfer to the
conjunction context, not evidence of arbitrary contextual generalization.
