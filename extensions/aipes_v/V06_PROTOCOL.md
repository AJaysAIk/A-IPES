# v0.6 frozen protocol: temporal model inadequacy

Freeze this protocol in GitHub before executing v0.6 outcomes. v0.5 remains a
recorded null incremental result and its code and data will not be retuned.

## Question
With an unchanged eight-model v0.5 hypothesis library, how quickly do acquisition
strategies discover (a) accepted uses that violate a temporal specification and
(b) observations incompatible with every remaining model? These are separate
outcomes. Does specification weighting add value when the library is inadequate?

## Fixed semantics and worlds
Actions remain grant, revoke, use, idle. Each trace resets state and contains
exactly six actions. All 4^6 = 4,096 traces form the candidate pool. The independent
public-history monitor now requires a grant, no intervening revoke, and grant
age <=2 at each accepted use. A grant sets age zero; every subsequent non-grant
action increments age before that action is judged. Regrant resets age. Refusing
a permitted use is not a safety violation (no liveness requirement).

Six world kinds, each with pulse off/on (12 deterministic worlds):
- compliant: accept only valid uses, lease expires after age 2; safe, out of class;
- premature: expire after age 1; safe, out of class;
- late: expire after age 3; unsafe, out of class;
- ignores_expiry: no expiration, otherwise obey grant/revoke; unsafe, in class;
- early: lease age 2, additionally accept uses before any grant; unsafe, out of class;
- stale: lease age 2, ignore revoke until lease expires; unsafe, out of class.
The nuisance pulse is emitted only on idle, as in v0.5.

The acquisition library remains exactly v0.5's eight early/stale/pulse models,
which have no lease clock. Predictions use those models with the new public
specification. The true world's switches and labels are never passed to a
selector. Exhaustive response-equivalence and violation checks over the candidate
pool must confirm the stated realizability and safety labels independently of
selection before aggregating results.

## Acquisition and costs
Four strategies: response entropy + 2.0*violation-label entropy
(specification_active), response entropy alone (transition_active), finite-model
counterexample_guided, and random. Uniform version-space prior, no likelihood
fitting and no retuning. Entropy uses stable summation over category counts.

For each seed, independently shuffle candidate order with Random(seed) and model
order with Random(seed+1000003). All strategies/worlds share the candidate order;
CEG uses that shuffled model order. CEG takes the first unqueried predicted
counterexample of the first remaining model with one, validates on the black box,
and filters with full observed responses. Information ties follow candidate order.

Filter the posterior after each observation. If it becomes empty, record a sticky
model_inadequate flag and its first query; never insert a fallback safe model,
never treat an empty posterior as vacuous proof of safety. Continue all remaining
queries in seeded candidate order after collapse, preserving equal call budgets.
Without a violation or mismatch, report no_counterexample_observed, not safe.

Budgets: 1,2,4,8 trace queries (6,12,24,48 action calls); seeds 0–19. Generate one
maximum trajectory and evaluate prefixes. No early stopping; resets counted
separately. Search is capped by the same 4,096 candidates and eight models for
all methods; this is equal black-box call budget, not equal CPU time. Cache model
predictions and scores; log logical candidates considered, prediction lookups and
CEG violation lookups per query so computational differences remain visible.

## Reporting and verification
Save all per-prefix rows and every query's trace, full response, actual monitor
result, posterior sizes, mismatch state, cumulative action calls/resets and search
work counters. Record first violation and first mismatch queries/calls separately;
undetected values are empty. Final status is violation_observed if one occurred,
otherwise model_inadequate_without_violation if collapsed, otherwise
no_counterexample_observed. No status claims safety.

Report detection by world kind and overall unsafe cases, mismatch detection among
out-of-class worlds, and false mismatch flags on in-class controls. Report safe
world violations separately from safe-world mismatches. Seeds change order and
are not independent sampled environments. Any follow-up tuning must be a new
protocol, not a replacement for these outcomes.

Tests: precise expiration boundary, revoke/regrant and early/stale histories,
independent monitor fixtures, exact mismatch detection including on safe worlds,
no empty-posterior safety claim, full oracle world labels, CEG ordering and
validation, paired seeds, reproducibility, nested prefixes, exact call accounting,
and saved evidence regeneration on Python 3.11 and 3.12.

## Limits
One small deterministic temporal family, known specification, free resets and a
fixed bounded search pool. Posterior collapse can reveal some misspecification;
a nonempty posterior cannot establish model adequacy. No general OOD detector,
formal unbounded verification, real-world safety, or research novelty is claimed.
