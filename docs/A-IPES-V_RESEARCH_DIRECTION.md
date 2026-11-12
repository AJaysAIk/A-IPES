# A-IPES-V doctoral research direction

## Status and evidence boundary

A-IPES-V is an implemented research extension of the A-IPES MSc dissertation. The repository currently contains:

- a specification-aware state-based experiment with held-out synthetic worlds;
- a bounded temporal adapter for grant, revoke, use, and idle histories;
- an independent finite-trace safety monitor;
- response-information, specification-information, random, and counterexample-guided acquisition strategies;
- frozen protocols, machine-readable results, query-level audits, tests, and dedicated reproducibility workflows.

The strongest current evidence is v0.5, a deterministic finite-model experiment over eight known temporal models and all 256 length-four traces. This is concrete implementation evidence, but it is not general formal verification, full LTL model checking, proof of deployed-agent safety, or validation on real Model Context Protocol agents.

See the [v0.5 protocol](../extensions/aipes_v/V05_PROTOCOL.md), [measured results](../extensions/aipes_v/V05_RESULTS.md), and [temporal implementation](../extensions/aipes_v/src/aipes_v/temporal.py).

## What v0.5 established

The v0.5 experiment studies discovery of accepted tool use without a currently valid grant. It evaluates six unsafe models and two safe controls across twenty seeded candidate orderings.

At a one-trace budget:

- specification-active acquisition detected 80 of 120 unsafe world-seed cases;
- response-information acquisition also detected 80 of 120;
- the counterexample-guided baseline detected 84 of 120;
- random acquisition detected 44 of 120.

By two traces, the three informed strategies detected all 120 unsafe cases. Specification entropy provided no incremental detection advantage over response entropy in this finite setting. All strategies produced zero safe-control alarms at every reported budget. These are repeated measurements of eight deterministic models, not independent real-world agents.

This null incremental result is part of the contribution. It shows that adding an explicit specification term does not automatically improve acquisition when response disagreement already identifies the relevant traces.

## Doctoral research question

How can specification-aware active runtime assurance remain useful when an agent's policy, environment, or behavioural model is uncertain, misspecified, non-deterministic, or strategically adaptive?

The doctoral problem is therefore not to claim that A-IPES-V already solves formal verification. It is to move from a small realizable finite class toward assurance methods whose assumptions, uncertainty, detection limits, and failure modes remain explicit in more realistic agent environments.

## Research gap

The existing v0.5 benchmark makes several strong assumptions:

1. the true system belongs to the known eight-model hypothesis class;
2. transitions are deterministic;
3. the candidate trace space is finite and exhaustively enumerable;
4. every adaptive strategy has equal access to the complete model class;
5. the monitor checks one bounded authorization property;
6. traces have fixed length four;
7. resets are available and excluded from the action-call budget;
8. the tested systems are synthetic models rather than deployed agents.

These assumptions create strong internal validity but limit external validity. The next research stage should deliberately break them one at a time.

## Proposed research objectives

### Objective 1  Model misspecification

Evaluate behaviour when the true agent is outside the evaluator's hypothesis class. Develop explicit unresolved or unknown outcomes instead of forcing every observation into an incorrect known model.

### Objective 2  Stochastic and partially observable behaviour

Replace deterministic transitions with stochastic responses and hidden context. Maintain calibrated uncertainty over candidate policies and specification satisfaction.

### Objective 3  Policy and objective drift

Introduce controlled changes in agent policy caused by context, model updates, prompt manipulation, tool compromise, or adaptive strategy. Compare sequential Bayesian and changepoint approaches using detection delay, false alarms, and calibration.

### Objective 4  Richer temporal specifications

Progress from one bounded authorization property toward multiple interacting safety properties, longer histories, and carefully selected temporal-logic fragments. Separate runtime monitoring from claims that require full model checking.

### Objective 5  Adversarial evaluation

Test whether an agent or compromised tool can recognise the evaluator, conceal unsafe behaviour, exploit the acquisition strategy, or induce distribution shift.

### Objective 6  Real agent traces

Move from finite synthetic models to reproducible local tool-using agents and sandboxed MCP environments. Preserve frozen protocols, matched budgets, query audits, and conservative claim boundaries.

## Candidate methods

Methods to investigate include:

- temporal logic and executable runtime monitors;
- probabilistic model checking where an adequate abstract model exists;
- Bayesian policy inference and posterior predictive checking;
- active learning and Bayesian experimental design;
- sequential changepoint detection;
- counterexample-guided trace generation;
- conformal or calibration-aware uncertainty estimates;
- adversarial and distribution-shift evaluation.

These are candidate methods, not claims of completed capability. Each should be retained only if it answers a defined research question better than a simpler baseline.

## Evaluation strategy

A staged programme should use:

1. misspecified variants of the existing finite benchmark;
2. stochastic and partially observable simulated tools;
3. recorded traces from reproducible local agents;
4. sandboxed live MCP agents under benign, shifted, and adversarial conditions.

Baselines should include:

- passive characterisation;
- random trace selection;
- response-information acquisition;
- specification-information acquisition;
- counterexample-guided search;
- monitoring without active acquisition;
- conventional active learning;
- an oracle or upper-bound selector where scientifically appropriate.

Primary outcomes should distinguish policy identification from safety assurance. Candidate measures include specification-violation recall, false-positive rate, detection delay, calibration, intervention cost, posterior contraction, unresolved-case rate, and robustness under misspecification.

## Threats to validity

The research must continue to address:

- abstraction mismatch between formal models and real agents;
- non-identifiability of latent objectives from behaviour;
- dependence between transformed or repeated traces;
- evaluator-induced behaviour changes;
- incomplete or biased safety specifications;
- adaptive agents that recognise the test;
- post-selection inference after adaptive acquisition;
- the difference between zero observed violations and a safety guarantee.

## Relationship to the MSc dissertation

The dissertation established a reproducible framework for budgeted intervention selection and showed a budget-dependent crossover between passive and adaptive policy identification. A-IPES-V changed the acquisition target from policy identification alone toward explicit safety-property evidence.

Version 0.5 then showed why this extension must be evaluated rather than assumed: specification weighting did not outperform response entropy, while a simple finite-model counterexample-guided baseline was competitive. The doctoral contribution must therefore come from handling harder assumptions and demonstrating when specification-aware acquisition changes what is tested, what can be inferred, or how quickly meaningful violations and policy shifts are detected.

## Next implementation milestones

1. Add an out-of-class temporal model and an explicit unresolved posterior outcome.
2. Introduce stochastic responses with calibrated likelihood-based refinement.
3. Randomise counterexample-guided model ordering and freeze a new protocol.
4. Extend trace length under a fixed action-call and compute budget.
5. Add controlled mid-run policy shifts and report censored detection delay.
6. Compare monitoring-only, information-driven, and counterexample-guided methods under matched access.
7. Transfer the frozen design to a sandboxed local MCP-agent environment.

These milestones extend completed v0.5 evidence; they are not yet completed results.
