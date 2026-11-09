# Prospectively reserved authority-contract evaluation

Fixed 6 November 2026 before evaluating selector outcomes on the purchasing
workflow. Engineering witness/unit tests are permitted for correctness. This is
an author-designed synthetic evaluation with prospective outcome reservation,
not externally collected held-out systems or an independent replication.

## Question and evidence boundary
Under a fixed executed-action budget, does monitored L* black-box checking expose
operational contract faults more effectively than monitored L* without property
checking, uniform random testing, or a straightforward fixed contract suite?
Do not assume a new acquisition method is needed or superior.

All strategies receive the same public action alphabet and contract. No tester
reads the true service state, fault label or ground-truth witness. A fixed suite
uses public contract semantics and is intentionally a strong simple baseline.
A-IPES's eight-model temporal selectors are not included: their library cannot
represent these services, so their earlier results remain separate.

## Systems and reservation
Document: existing SQLite implementation, correct/stale_revision/expired_approval/
role_bypass fixtures previously used in development, plus ignored_revocation (new
fixture). Purchase: separately implemented Python service, not importing document
transition logic; correct/scope_binding/identity_binding/ignored_revocation/
role_bypass fixtures. No purchase selector outcomes have been inspected when
this protocol is fixed. Fault families are chosen in advance, not unknown to the
study designer. Report the development document fixtures separately.

Document contract is unchanged: verified evidence and approval bound to the current
revision; approval age <=3, no revoke; executor only. Purchase contract: supplier
check, reviewer approval bound to supplier and requester identity, no revocation,
executor-only payment. Supplier/requester toggles are reversible; returning to an
original approved scope permits reuse unless revoked. Purchase has no expiry.
Outputs are structured ok/denied/committed, not natural-language agent messages.

## Fixed strategies and settings
AALpy 2.0.0 L* Mealy learner; RandomWMethodEqOracle walks_per_state=10, walk_len=6.
BBC wraps that oracle in BBCEqOracle with product-state breadth-first property
search bounded to depth six. Model-only search has no real-call cost; record its
edge count and wall time. No-BBC uses the same learner and W oracle. Monitor every
actual action in both. If the approximate oracle terminates early, fill the cap
with random six-action traces; label this suffix and never claim convergence.

Random tester: independent uniform actions, reset after six actions. Contract
suite: the following six traces, once each, then the same random suffix; no fault-
specific branches. Document traces (v=verify,a=approve,e=execute,r=reviewer_execute):
[v,a,e]; [e]; [v,a,r]; [v,a,revoke,e]; [v,a,edit,e];
[v,a,idle,idle,idle,e]. Purchase traces (v=check,a=approve,e=pay,r=reviewer_pay):
[v,a,e]; [e]; [v,a,r]; [v,a,revoke,e]; [v,a,change_supplier,e];
[v,a,switch_requester,e]. All suites derive from public requirements.

Seeds 0–9. Candidate/oracle random streams seeded per run; suffix Random(seed)
identical across strategies. Budgets 250,1000,2000 executed calls. Generate each
maximum run once and evaluate nested call prefixes. Continue after violations;
no early stop. At cap, interrupt before the next actual action, preserving the
last observed prefix; do not fabricate an incomplete query's output. Resets
counted separately, including library-requested resets even when no call follows.
Capture cache counters where available; unavailable values remain null, not zero.

## Outcomes and accounting
Primary: observed violation within each executed-call prefix, first violating
call (empty if censored), per fixture and strategy. Cases are ten order seeds of
one deterministic fixture; no binomial population inference. Report by workflow
and fixture, not only pooled totals. Safe controls: violation flags. Utility:
number of contract-permitted attempts, permitted commits and their ratio when
nonzero; this is conditional on the chosen test distribution, not task completion.
Report attempted clause challenges and clauses with observed violations.

Audit each actual call: action, output, reset/query prefix, phase, independent
monitor verdict, failed contract clauses and permission. Phases distinguish learner,
equivalence testing, property-counterexample validation, suite and random suffix.
Save immutable compressed action logs, prefix rows, run summaries, source hashes,
environment, protocol hash and wall time. Keep logical model work separate from
actual calls. Byte-compare deterministic evidence on reproduction; wall time is
expected to differ. Failed runs must be recorded rather than dropped.

## Checks and stop rule
Test safe controls, planted witnesses, reversible scope changes, duplicate/expired
approval cases, role separation, revocation, phase accounting, exact cap, prefix
nesting and standard BBC rejection of spurious model counterexamples. Replay every
saved action independently against the service and monitor, and recompute prefix
outcomes. All strategies must operate through one audited adapter.

No tuning after outcomes. Errors affecting semantics or selection require a
versioned amendment and preserved results, not silent replacement. If simple suite
coverage saturates the faults, report that benchmark limitation and stop adding
methods. No ATC reproduction, natural-language contract validation, deployment
safety, algorithmic novelty, or generalization claim follows from this evaluation.
