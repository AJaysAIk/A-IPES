# Phase 1: Equal-budget probe-selection experiment

## Purpose

Test whether the active selector discovers safety-relevant tool effects more efficiently than fair alternatives under the same intervention budget.

## Strategies

1. `single_default`: one default-state intervention.
2. `random`: random states from the same candidate pool.
3. `fixed_boundary`: deterministic states ranked by policy-boundary relevance.
4. `active`: ensemble disagreement + policy-boundary relevance + novelty.

## Budgets

`1, 2, 3, 5, 8, 10` interventions per tool.

## Primary endpoint

Unsafe-action recall on shifted interfaces, subject to benign false-positive rate.

## Mechanism endpoint

Mean absolute error of predicted post-action policy state across the full candidate-state pool.

## Interpretation

A useful pilot result is not simply that active probing has the highest recall. It should show one or both of:

- lower effect-prediction error at the same budget;
- equal detection performance with fewer interventions.

If fixed boundary probes match active probing, active learning may not be necessary in this small domain. That is an informative falsification, not a reason to manipulate the benchmark.
