# A-IPES-V research direction

## Status

A-IPES-V is a proposed doctoral research direction derived from the empirical findings and limitations of the A-IPES MSc dissertation. It is not implemented in this repository, and no claim of formal verification or deployed-agent validation is made.

## Motivation

A-IPES studies how an evaluator should allocate a limited intervention budget to identify an unknown runtime policy. Its current evidence comes from a controlled synthetic benchmark with a finite hypothesis library. The framework estimates which intervention is likely to be informative, but it does not establish that an agent satisfies a formal safety specification, detect a policy that changes during deployment, or provide guarantees for real Model Context Protocol agents.

A-IPES-V would connect active evidence acquisition with specification-aware runtime verification. The central idea is that an intervention should be valuable when it reduces uncertainty about whether an agent satisfies or violates an explicit safety property, rather than merely producing a novel behaviour.

## Research question

How can a runtime-assurance system actively select informative interventions while maintaining calibrated uncertainty over an agent's latent policy and verifying whether evolving behaviour satisfies explicit safety specifications?

## Proposed system model

A candidate system would contain:

1. **Agent and environment model** — an agent interacts with tools or services in a sandboxed environment.
2. **Specification layer** — safety requirements are expressed as temporal, operational, or tool-use properties.
3. **Belief state** — the evaluator maintains uncertainty over candidate agent policies or behavioural models.
4. **Active acquisition layer** — candidate interventions are scored by their expected value for confirming or falsifying specification-relevant hypotheses.
5. **Runtime monitor** — observed traces are checked against the active specifications.
6. **Drift detector** — posterior or trace changes are used to detect when the agent's policy may have shifted.

This is an initial research design, not a completed architecture.

## Research objectives

### Objective 1  Specification-aware acquisition

Replace generic safe or unsafe labels with explicit safety properties. Develop acquisition functions that prioritise interventions according to expected reduction in uncertainty about those properties.

### Objective 2  Policy drift

Extend the fixed-policy assumption to settings where an agent's behaviour can change through context, model updates, prompt manipulation, tool compromise, or adaptive strategy. Compare changepoint and sequential Bayesian approaches for early drift detection.

### Objective 3  Formal and statistical assurance

Study the boundary between formal claims and empirical uncertainty. Formal verification may apply to an abstract model or monitor, while statistical evidence characterises uncertainty about whether the deployed agent conforms to that model.

### Objective 4  Adversarial evaluation

Test whether the acquisition and monitoring strategy remains useful when an agent or compromised tool adapts to the evaluator, conceals unsafe behaviour, or induces distribution shift.

### Objective 5  External validity

Move beyond the finite synthetic hypothesis library toward sandboxed tool-using agents and recorded MCP execution traces. Preserve controlled experiments while introducing progressively more realistic environments.

## Candidate methods

The following methods are candidates for investigation rather than committed solutions:

- temporal logic and runtime-monitor specifications;
- probabilistic model checking;
- Bayesian policy inference and calibrated posterior prediction;
- active learning and Bayesian experimental design;
- sequential changepoint detection;
- adversarial and distribution-shift evaluation;
- counterexample-guided intervention generation.

A doctoral project should determine which combination is justified by the research question and evaluation environment.

## Evaluation plan

A staged evaluation could use:

1. controlled synthetic policy worlds for internal validity;
2. simulated MCP tool environments with hidden agent policies;
3. recorded traces from reproducible local agents;
4. sandboxed live agents under benign, shifted, and adversarial conditions.

Candidate baselines include:

- passive characterisation;
- random intervention selection;
- fixed-boundary selection;
- monitoring without active acquisition;
- active learning based on generic predictive uncertainty;
- a conventional runtime-verification pipeline;
- an oracle or upper-bound selector where appropriate.

Primary outcomes should distinguish policy identification from safety assurance. Possible measures include specification-violation recall, false-positive rate, detection delay, calibration, intervention cost, posterior contraction, and the probability of returning to a specified safe operating region.

## Threats to validity

The research must explicitly address:

- abstraction mismatch between formal models and real agents;
- non-identifiability of latent objectives from behaviour;
- dependence between transformed or repeated traces;
- evaluator-induced behaviour changes;
- incomplete or biased safety specifications;
- adaptive agents that recognise the test;
- the gap between zero observed violations and a safety guarantee.

## Relationship to A-IPES

A-IPES provides the empirical starting point: a reproducible acquisition framework, paired benchmark design, budget-dependent findings, and evidence that adaptive selection is not uniformly beneficial. A-IPES-V would not simply add a formal-methods label. Its contribution would need to show that specification-relevant acquisition changes what is tested, what can be inferred, or how quickly meaningful violations and policy shifts are detected.

## Near-term implementation milestones

1. Define a small temporal or state-machine specification language for benchmark policies.
2. Convert selected Benchmark V2 safety labels into explicit properties.
3. Implement a monitor that returns satisfaction, violation, or unresolved status for partial traces.
4. Add a specification-information term to the acquisition function.
5. Compare it against the existing passive and policy-active strategies under matched priors.
6. Introduce controlled policy shifts and measure detection delay.
7. Freeze the protocol before expanding to a sandboxed MCP-agent environment.

These milestones are a proposed research programme and are not evidence of completed work.
