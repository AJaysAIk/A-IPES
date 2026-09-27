# Phase 3 Findings: Passive Characterisation Baseline

## Objective

Compare policy-aware active probing against a literature-inspired,
non-adaptive passive characterisation baseline under equal intervention
budgets.

## Main finding

At intervention budget 3, policy-active probing achieved:

- attack recall: 0.9354
- false-positive rate: 0.0052
- F1: 0.9628
- balanced accuracy: 0.9651
- policy exact match: 0.9648
- effect MAE: 0.0298
- shifted attack recall: 0.9288

The passive characterisation baseline achieved:

- attack recall: 0.9077
- false-positive rate: 0.0000
- F1: 0.9516
- balanced accuracy: 0.9538
- policy exact match: 0.9630
- effect MAE: 0.0401
- shifted attack recall: 0.8983

Policy-active probing therefore produced its clearest advantage at budget
3. At budget 5, active and passive characterisation converged on most
downstream policy metrics.

## Interpretation

The evidence supports a constrained-budget claim:

Policy-aware active intervention selection is most useful when the number
of permitted probes is small to moderate. Its advantage diminishes once
passive characterisation receives enough observations.

## Limitation

The current seed changes primarily affect random probe selection. Several
deterministic strategies have zero variance across seeds. Therefore, the
30 executions are not 30 independent benchmark samples and must not yet
be used as independent observations for significance testing.

The next benchmark version must vary tool families, effect parameters,
policy states, mutations, descriptions, and train/test splits across
benchmark seeds.
