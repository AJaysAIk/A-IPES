# Phase 3: Literature-inspired passive characterisation baseline

## Purpose

Add a non-adaptive external-style baseline to the Phase 2 evaluation. The
baseline follows the progressive passive characterisation philosophy described
by ToolGuardian: begin with declared metadata and then observe fixed execution
traces. It is not a reproduction of ToolGuardian's ASP policy engine or full
characterisation stack.

## Baseline definition

`passive_characterisation` uses:

1. a coarse effect-family prior inferred from the tool name and description;
2. a fixed, tool-independent sequence of execution states;
3. the same transition-hypothesis learner and evaluator used by the other
   strategies;
4. no posterior-dependent or uncertainty-dependent probe selection.

This isolates the research question: whether policy-aware adaptive probe
selection is more sample-efficient than passive non-adaptive characterisation
under an equal intervention budget.

## Academic wording

Use:

> We implement a literature-inspired passive characterisation baseline based on
> the progressive evidence-acquisition philosophy of ToolGuardian. The baseline
> is a controlled abstraction rather than a full reimplementation.

Do not write that this code reproduces ToolGuardian.
