# v0.5 protocol: bounded temporal counterexample discovery

Frozen before running v0.5 outcomes. This is a new finite-trace adapter of the
A-IPES-V acquisition principle, not the unchanged v0.4 state selector.

## Question and semantics
Can specification disagreement improve discovery of an accepted `use` without a
currently valid grant, compared with response-information acquisition, random
traces, and a counterexample-guided finite-model baseline?

Every query resets the black box to ungranted, then executes exactly four actions
from {grant, revoke, use, idle}. A grant authorizes subsequent use; revoke removes
authority. The monitor tracks authority from the action history, independently
of the tool's internal state. Safety requires every accepted use to have a valid
grant at that point. This is a bounded safety property, not liveness or full LTL.

The finite model class is the Cartesian product of three Boolean switches:
accept use before any grant; retain authority after revocation; emit an irrelevant
pulse on idle. All eight models are evaluated as worlds. Two are safe controls;
six violate the specification on at least one candidate trace. The pulse is an
observable nuisance effect. The complete candidate pool is all 256 length-four
traces. Truth labels and true switch settings are never supplied to acquisition.

## Fixed methods and budget
All methods begin with the same uniform eight-model version space and candidate
pool, without replacement. After each query, retain exactly the models matching
the complete response sequence. Empty posteriors raise an error, not a safe default.

- specification_active: response entropy + 2.0 * entropy of the predicted Boolean
  trace-violation label; expected-violation weight remains zero.
- transition_active: response entropy alone, an information-only temporal
  adaptation; it is not claimed to be the original policy-active A-IPES algorithm.
- counterexample_guided: choose the first remaining model (canonical model order)
  with an unqueried predicted counterexample, then its first counterexample in a
  seeded candidate order. Validate on the actual tool and refine with all observed
  responses. If no such model remains, explore the next candidate in that order.
  This is a finite-model CEG baseline, not a full CEGAR implementation.
- random: choose the next trace in the same seeded candidate order.

Entropy uses a uniform empirical distribution over remaining models. Entropy ties
use the same seeded candidate order for all methods and worlds within a seed.
No early stopping: every query costs four action executions; resets are counted
separately as one per trace. Budgets are 1, 2, 4, 8 trace queries (4, 8, 16, 32
calls). Seeds are 0–19. Each maximum-budget trajectory is evaluated by prefixes.

## Reporting and checks
Save all per-world/strategy/seed/budget rows and each queried trace with its
responses, monitor result, posterior size and cumulative action-call count.
Report detection numerators/denominators, safe-control alarms, and censored
first-detection query/call counts (undetected values remain empty). Report each
unsafe mutant class separately as well as aggregate detection. Seeds vary order,
not independently sampled worlds; do not use them to claim population coverage.

Tests must cover grant/use, use before grant, grant/revoke/use, regrant, monitor
independence, model elimination, counterexample validation, reproducibility,
prefix nesting and exact call accounting. An exhaustive oracle checks all 256
traces to validate world labels independently of acquisition. No tuning after
outcomes; any change affecting design must be disclosed as a protocol amendment.

## Boundaries
The true tools are in the known tiny hypothesis class, execution is deterministic,
resets are free in the call budget, and only one temporal authorization family is
studied. Equal model access intentionally makes CEG strong. A null result or CEG
advantage is scientifically useful. No claim of novel model checking, general
agent safety, real-world transfer, or statistical generalization is warranted.
