# A-IPES Code Traceability Map

**Project:** Adaptive Intervention Planning for Efficient Runtime Policy Identification (A-IPES)

This document maps each scientific contribution in the dissertation to the corresponding implementation in the source code. Its purpose is to ensure complete traceability between the research claims, algorithms, experiments, and implementation.

---

# 1. Overall Architecture

A-IPES consists of four major components:

1. Runtime policy hypothesis representation
2. Adaptive acquisition (probe selection)
3. Benchmark V2 evaluation framework
4. Statistical analysis and ablation

---

# 2. Core Algorithm

## File

src/ipes_guard/policy_active.py

### Purpose

Implements the A-IPES adaptive intervention algorithm.

### Key Responsibilities

- Represent candidate runtime policy states
- Maintain policy hypotheses
- Compute acquisition scores
- Select the next intervention
- Return ordered probe selections

---

## Main Functions

### build_hypothesis_library()

Purpose:

Creates the hypothesis space representing possible runtime policies.

Research contribution:

Provides the candidate policy set over which adaptive intervention planning operates.

---

### _boundary_score(state)

Purpose:

Measures how informative a probe is relative to decision boundaries.

Scientific role:

Encourages interventions near uncertain policy transitions.

---

### _novelty_score(state, selected)

Purpose:

Rewards probes that provide information different from previously selected probes.

Scientific role:

Reduces redundant interventions.

---

### acquisition_score(...)

Purpose:

Computes the overall acquisition value for every candidate intervention.

Scientific role:

Implements the A-IPES acquisition function by combining multiple information sources.

---

### select_policy_active_probes(...)

Purpose:

Core A-IPES algorithm.

Scientific role:

Iteratively selects the most informative runtime interventions under a constrained budget.

This function represents the primary implementation of A-IPES.

---

# 3. Benchmark Framework

## File

src/ipes_guard/benchmark_v2.py

Purpose:

Implements Benchmark V2.

Responsibilities:

- Generate benchmark worlds
- Execute all competing strategies
- Collect evaluation metrics
- Save experiment outputs

Strategies evaluated:

- single_default
- passive_characterisation
- random
- fixed_boundary
- policy_active

---

# 4. Phase 2 Benchmark

## File

src/ipes_guard/phase2_benchmark.py

Purpose:

Earlier benchmark framework used during development.

Responsibilities:

- Integrates A-IPES into policy probe experiments.
- Executes comparative strategy evaluations.

---

# 5. Experiment Scripts

## scripts/run_benchmark_v2.py

Purpose:

Runs Benchmark V2 experiments.

Outputs:

- summary.csv
- per_benchmark.csv
- raw.csv
- benchmark_manifests.csv
- selected_probes.csv

---

## scripts/run_phase2_policy_probe_experiment.py

Purpose:

Runs Phase 2 policy probe experiments.

---

# 6. Statistical Analysis

## scripts/analyse_benchmark_v2.py

Purpose:

Performs statistical analysis.

Includes:

- paired comparisons
- confidence intervals
- sign-flip tests
- summary statistics

---

# 7. Acquisition Ablation

Implemented through the parameterised acquisition framework.

Variants evaluated:

- policy_active_full
- policy_active_no_policy
- policy_active_no_boundary
- policy_active_no_outcome
- policy_active_no_novelty

Purpose:

Quantifies the contribution of each acquisition mechanism.

---

# 8. Experimental Evidence

Benchmark V2 evaluates:

- Attack Recall
- False Positive Rate
- Precision
- F1 Score
- Balanced Accuracy
- Policy Exact Match
- Effect MAE
- Shifted Attack Recall
- Posterior Reduction Ratio
- Information Gain

Statistical evaluation includes:

- 30 benchmark worlds
- confidence intervals
- paired analysis
- sign-flip testing
- acquisition ablation

---

# 9. Scientific Contribution Mapping

| Scientific Contribution | Implementation |
|-------------------------|----------------|
| Runtime policy hypothesis formulation | policy_active.py |
| Adaptive intervention planning | select_policy_active_probes() |
| Acquisition function | acquisition_score() |
| Boundary mechanism | _boundary_score() |
| Novelty mechanism | _novelty_score() |
| Benchmark V2 | benchmark_v2.py |
| Comparative evaluation | run_benchmark_v2.py |
| Statistical analysis | analyse_benchmark_v2.py |
| Acquisition ablation | Parameterised acquisition framework |

---

# 10. Dissertation Traceability

Chapter 3 (Methodology)
→ policy_active.py

Chapter 4 (Experimental Design)
→ benchmark_v2.py

Chapter 5 (Results)
→ Benchmark V2 outputs

Chapter 6 (Ablation Analysis)
→ Acquisition ablation experiments

Chapter 7 (Discussion)
→ Statistical analysis and empirical findings

---

This document provides a complete mapping between the scientific claims presented in the dissertation and the corresponding implementation within the A-IPES codebase.
