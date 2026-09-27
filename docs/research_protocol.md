# Research protocol: IPES-Guard

## Central claim

Counterfactual, intervention-derived policy-effect signatures are more invariant to tool-interface mutation than name-based or text-semantic representations, enabling stronger unsafe-trajectory detection at a matched false-positive rate.

## Main research question

Do interventional policy-effect signatures reduce the degradation in unsafe-action detection under unseen names, schemas, descriptions, and deceptive aliases compared with manual state abstractions, text-semantic detectors, single-state observed-effect characterisation, and an AgentGuard-style trajectory baseline?

## Hypotheses

- **H1 — Interface invariance:** IPES produces a smaller mutation gap than all non-interventional baselines.
- **H2 — Safety–utility:** At a fixed benign false-positive ceiling, IPES obtains higher unsafe-trajectory recall on tool-disjoint test interfaces.
- **H3 — Mechanism:** Removing counterfactual probe diversity or obligation-aware policy evaluation materially reduces performance.
- **H4 — Uncertainty:** A calibrated plausible-effect set lowers catastrophic false allows on unfamiliar effects while preserving benign completion.

## Primary endpoint

Unsafe-trajectory recall on a frozen tool-family-disjoint and mutation-disjoint test set, measured at a benign false-positive rate no greater than 5%.

## Secondary endpoints

- mutation gap: recall(seen interface) - recall(mutated interface);
- area under the precision–recall curve;
- benign task completion rate;
- detection delay in actions;
- effect-model state-variable F1 / MAE;
- conformal set coverage and set size;
- median and p95 runtime latency.

## Required baselines

1. exact tool-name/manual mapping;
2. manual semantic action classes;
3. text-only E5 or sentence-transformer classifier;
4. single-probe observed-effect characterisation;
5. AgentGuard-style manually abstracted MDP/PRISM or Storm baseline;
6. rule-only trace monitor inspired by C-Trace;
7. full IPES.

Do not call a reimplementation an official implementation. Label it “paper-faithful reproduction” and document every divergence.

## Dataset design

Target for the final dissertation:

- 40–60 base tool implementations;
- 3–5 interface mutations per tool;
- 8–12 policy-effect classes;
- 8–12 counterfactual probe states;
- 100–150 independent trajectories;
- at least four unsafe mechanism families;
- frozen train/validation/test splits by base tool family.

Mutations:

- renaming;
- description paraphrase;
- argument-schema shift;
- deceptive benign alias;
- similar-looking benign tool;
- hidden conditional effect;
- multi-tool composition.

## Statistical analysis

- Unit of analysis: independent tool/scenario, not deterministic replay seed.
- Report bootstrap 95% confidence intervals.
- Use McNemar’s exact test for paired detector decisions.
- Use Wilcoxon signed-rank or paired bootstrap for detection delay.
- Correct multiple primary pairwise comparisons using Holm’s procedure.
- Report absolute effects, not p-values alone.
- Training seeds quantify optimisation variance; they do not create independent scenarios.

## Ablations

- one probe state only;
- random rather than boundary-focused probes;
- no obligation ledger;
- no role context;
- text-only interface representation;
- exact effects without quotient grouping;
- no conformal uncertainty;
- no trajectory history.

## Falsification criteria

The hypothesis is not supported if any of the following holds:

- a text-only baseline matches IPES on the frozen deceptive-interface test;
- multi-probe characterisation does not outperform single-probe characterisation;
- the mutation gap is not materially reduced;
- gains disappear after matching false-positive rate;
- performance depends on test tools being present during training;
- the result occurs only in one hand-authored attack template.
