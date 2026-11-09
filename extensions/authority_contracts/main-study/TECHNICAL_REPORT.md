# Authority contracts under a fixed test budget

A-IPES-V follow-up | Working research report | 6 November 2026

## Summary

This study compares four ways to test operational authority contracts: monitored automata learning with black-box checking (BBC), the same learner without property checking, uniform random testing, and a fixed contract test suite. The systems are a SQLite document-approval service and a separately implemented mock purchasing service. The faults are deliberately injected; neither system is a live LLM agent.

Across 400 runs, every method received a cap of 2,000 actual service actions. Prefix outcomes were recorded at 250, 1,000 and 2,000 calls. The record contains 800,000 action events and 1,200 prefix rows. A separate replay pass checked every action and verdict; a second full execution reproduced the deterministic artifacts byte for byte.

## Main findings

The fixed contract suite detects all four unsafe fixtures in each workflow within 250 calls, for every tested seed. BBC reaches the same coverage by 1,000 calls. In the purchasing workflow, BBC and monitored learning alone have identical reported detection counts, and all first detections occur during learning. In the document workflow, property-counterexample validation consistently reveals the expiry defect that learning alone detects less often.

The evidence supports a narrow, useful conclusion: explicit contract tests are already sufficient for these shallow planted faults, while the incremental value of property checking is concentrated in one development fault family. It does not establish a need for a more elaborate acquisition method or a general BBC advantage.

## Research motivation and boundary

Earlier A-IPES-V experiments found that information-based selection can exhaust uncertainty inside a small assumed model class while missing behaviour outside it. This study replaces the finite-model heuristic with a recognised learner and a strong simple baseline. Learning, checking and refinement are established methods [1-4]; the present contribution is a reproducible controlled comparison and failure analysis, not a new verification algorithm.

The connection to agent-contract research is complementary. ATC studies role-contract enforcement at message boundaries [5]. The present study tests structured operational permissions and does not reproduce ATC, test its classifier, or demonstrate a weakness in that system.

# Design, controls and accounting

## Two implementations

Document approval: a SQLite-backed service tracks revision, verified evidence, approval revision and logical time. Committing requires an executor, approval/evidence tied to the current revision, no effective revocation, and approval age at most three. Four fixtures were previously used in development; ignoring revocation is a new fixture.

Purchasing: a separate Python implementation tracks supplier, requester, supplier check and an approval receipt. Payment requires the executor role and approval bound to the current supplier and requester. Supplier and requester changes are reversible; return to an approved scope permits reuse unless revoked. This workflow has no expiry constraint. Its selector outcomes were reserved until the protocol was fixed.

## Four strategies

| Strategy | Definition |
|---|---|
| BBC + learner | AALpy 2.0.0 L* Mealy learning; Random W oracle; BBCEqOracle with a custom depth-six product checker. |
| Learner only | The same learner and Random W oracle, without property checking. Every real action is still monitored. |
| Contract suite | Six public-contract traces, once each, then random testing. No fault-specific selection branches. |
| Random | Uniform inputs in reset traces of six actions. |

Random W settings are ten walks per state and maximum random-walk length six. All methods receive the same public alphabet and contract. If the approximate equivalence oracle terminates early, learning methods spend the remaining cap on a labeled random suffix. No completion or correctness guarantee is inferred.

## Costs and reservation

All actual actions from learning, equivalence testing and counterexample replay count toward the same cap. Cache hits execute no service action. Resets are recorded separately. Model-only checking incurs no action-call cost; its logical edge count and wall time are separate. An interrupted query retains its observed prefix without inventing an output sequence.

The design uses seeds 0-9 and one maximum trajectory per fixture/method/seed, evaluated by nested call prefixes. The protocol was locally hashed before evaluation; this is not external preregistration. All faults and contracts were designed by the study author. A prospectively reserved synthetic workflow is not an independently sampled population.

# Measured detection outcomes

Each cell is the number of unsafe fixture-seed cases detected, out of 40: four unsafe fixtures times ten ordering seeds. The denominator is not 40 independent implementations. The document cohort mixes development fixtures and one new fixture; the purchasing cohort was prospectively reserved.

## Document workflow: detections / 40

| Method | 250 calls | 1,000 calls | 2,000 calls |
|---|---|---|---|
| BBC + learner | 10 | 40 | 40 |
| Learner only | 10 | 33 | 34 |
| Contract suite | 40 | 40 | 40 |
| Random | 12 | 24 | 30 |

## Purchasing workflow: detections / 40

| Method | 250 calls | 1,000 calls | 2,000 calls |
|---|---|---|---|
| BBC + learner | 0 | 40 | 40 |
| Learner only | 0 | 40 | 40 |
| Contract suite | 40 | 40 | 40 |
| Random | 9 | 20 | 26 |

## Expiry isolates the incremental document result

| Document expiry only | 250 calls | 1,000 calls | 2,000 calls |
|---|---|---|---|
| BBC + learner | 0/10 | 10/10 | 10/10 |
| Learner only | 0/10 | 3/10 | 4/10 |
| Contract suite | 10/10 | 10/10 | 10/10 |
| Random | 0/10 | 0/10 | 2/10 |

For stale revision, ignored revocation and role bypass, both learning configurations detect 10/10 cases by 1,000 calls. All purchasing defects also reach 10/10 for both learning configurations by that budget. These patterns limit the incremental BBC claim to the document expiry fixture in this evaluation.

Both correct controls produce zero observed violation flags for every method and budget. This is a correctness check on the evaluated traces, not a population false-alarm guarantee. Undetected first-violation fields remain empty. No detected-only mean is used to imply complete time-to-detection coverage.

# Mechanisms, utility and validity limits

## Where first detections actually occur

| Workflow / method | First-event phase counts at 2,000 calls |
|---|---|
| Document / BBC | 30 during learning; 10 during property validation |
| Document / learner only | 30 learning; 3 equivalence testing; 1 random suffix; 6 missed |
| Purchase / BBC | 40 during learning |
| Purchase / learner only | 40 during learning |
| Contract suite / each workflow | 40 during the fixed suite |

These phase labels prevent attributing a detection to model checking merely because a BBC wrapper was present. The purchasing result offers no observed first-detection contribution from the property checker. For document expiry, the BBC property-validation phase supplies the additional detections.

## Legitimate operations

At the 2,000-call cap, permitted commits equal permitted attempts for every strategy. Document counts are BBC 2,026/2,026; learner-only 1,774/1,774; suite 590/590; random 540/540. Purchase counts are 1,239/1,239; 1,239/1,239; 465/465; 415/415 respectively. These sum over all five fixtures and ten seeds in each workflow. They show that tested legitimate operations were accepted, not end-to-end task success or comparable utility distributions.

## Limits that materially affect interpretation

Only two separately coded deterministic implementations are studied. The faults are shallow, known to the designer and directly tied to explicit contract clauses. The fixed suite was constructed from those public clauses, so its full coverage exposes benchmark simplicity rather than a novel testing result. No natural-language interpretation, external authorization system, concurrent execution or live agent behaviour is tested.

Ordering seeds are repeated observations of the same fixtures; no population significance test is justified. The approximate equivalence oracle may stop with an incorrect model. At 2,000 calls, 8/50 document and 5/50 purchasing runs in each learning configuration still exhaust the cap during learning. Even a returned model is not certified correct. The custom model checker is bounded to six actions, and the cost comparison equalises executed actions rather than CPU time or resets.

Replay uses the same service and public-monitor implementations in a separate pass, supported by independent monitor fixtures in tests. It is not evaluation by an independently developed judge. The protocol is locally hashed, not publicly timestamped preregistration. These distinctions should remain explicit in any external report.

# Reproduction and research implications

## Evidence package

The package contains the protocol and its SHA256 hash, two service implementations, the learner/BBC adapter, seven study tests, compressed action logs, prefix outcomes, run telemetry, wall times and source hashes. Five earlier feasibility tests also pass. A separate verifier replayed 800,000 actions and recomputed all 1,200 prefix records. A second full run matched prefixes, compressed logs, telemetry and provenance byte for byte; wall times are intentionally excluded from that comparison.

python run_study.py --output /new/results-directory
python verify_and_summarise.py /new/results-directory

Run these commands from the main-study directory in an environment using the pinned requirements in the parent package. Existing result directories are rejected. Record current source hashes and environment; do not silently replace the fixed protocol or existing results.

## What this supports for a research conversation

The strongest evidence is methodological: the study introduces a recognised baseline, charges every real query, includes a simple control that outperforms the elaborate methods here, and identifies where a checker actually contributes. It supports discussing the boundary between learning behaviour and testing contract adequacy. It does not support a claim that a new acquisition rule is needed or that agent safety has been established.

The appropriate next decision is to seek critique of the question and testbed, rather than add another score to these saturated fixtures. A later study could investigate deeper composition, partial observation or concurrent authority changes, but only under a new protocol with independent implementation evidence. No such result is claimed here.

## Selected primary references

[1] D. Angluin. Learning Regular Sets from Queries and Counterexamples (1987). [Original paper](https://people.eecs.berkeley.edu/~dawnsong/teaching/s10/papers/angluin87.pdf).

[2] D. Peled, M. Y. Vardi and M. Yannakakis. Black Box Checking (1999). [Author-hosted paper](https://www.cs.rice.edu/~vardi/papers/pstv99.pdf).

[3] A. Groce, D. Peled and M. Yannakakis. Adaptive Model Checking (2002). [Author-hosted paper](https://agroce.github.io/tacas02.pdf).

[4] AALpy v2.0.0. [Official release and library baseline](https://github.com/DES-Lab/AALpy/releases/tag/v.2.0.0).

[5] M. Maliha, V. Pramanik and S. K. Jha. ATC: Agent Trajectory Control for Role-Contract Enforcement in Black-Box Multi-Agent Systems (2026). [Author preprint](https://arxiv.org/html/2611.04321v1).

Prepared with AI assistance. Applicant contribution, understanding and interpretation must be reviewed before external circulation. This working report has not been peer reviewed.
