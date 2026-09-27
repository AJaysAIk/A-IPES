# Phase 2: Policy-aligned active probing

## Why Phase 1 is insufficient

The Phase 1 pilot saturates attack recall for every multi-probe strategy while producing false-positive rates between roughly 0.18 and 0.73. Raw state-vector MAE is therefore not aligned with the runtime safety decision. The active strategy reduces MAE at budgets 3 and 5, but that reduction does not translate into a better recall/FPR trade-off.

## Phase 2 correction

Phase 2 changes both the estimator and benchmark while keeping probe budgets equal.

1. **Conditional effects:** tools reveal effects only in particular policy states.
2. **Disjoint evaluation states:** probe states use resource values 0 and 5; evaluation uses 1, 4, and 6.
3. **Same estimator for all strategies:** every strategy filters the same generic transition-hypothesis library.
4. **Policy-aware active selection:** candidate probes maximise transition-outcome entropy and safe/unsafe policy entropy, with small boundary and diversity terms.
5. **Policy metrics:** report attack recall, FPR, precision, F1, balanced accuracy, exact violation-code agreement, shifted-interface recall, effect MAE, and posterior size.

## Falsifiable hypothesis

At equal intervention budgets, policy-active probing should achieve higher balanced accuracy and policy exact-match than random and fixed-boundary probing, without increasing FPR.

## Interpretation rule

Do not claim success from recall alone. A useful result requires simultaneous improvement in policy exact-match or balanced accuracy and a controlled false-positive rate. If fixed-boundary probing remains better, the active acquisition function has not earned its complexity.
