"""Paired sensitivity study for non-redundant specification acquisition.

Weights are varied without changing the worlds, candidate pool, or random seeds.
This is a robustness diagnostic, not an independent held-out benchmark.
"""
from __future__ import annotations

from collections.abc import Sequence

from ipes_guard.policy_active import select_policy_active_probes

from .acquisition import (
    SpecificationAcquisitionWeights,
    select_specification_aware_probes,
)
from .nonredundant import _evaluate, candidate_states, verification_worlds


def run_weight_sensitivity(
    weights: Sequence[tuple[float, float]] = (
        (0.0, 0.0),
        (0.5, 0.0),
        (1.0, 0.0),
        (2.0, 0.0),
        (2.0, 0.5),
        (4.0, 1.0),
    ),
    seeds: Sequence[int] = tuple(range(10)),
    budgets: Sequence[int] = (1, 2),
) -> list[dict]:
    pool = candidate_states()
    budgets = tuple(sorted(set(budgets)))
    if not budgets or min(budgets) < 1 or max(budgets) > len(pool):
        raise ValueError("Invalid budgets")
    rows = []
    for world in verification_worlds():
        for seed in seeds:
            baseline = select_policy_active_probes(
                world.tool, max(budgets), pool, random_state=int(seed)
            ).selected_states
            for budget in budgets:
                result = _evaluate(world, baseline[:budget])
                rows.append({
                    **result,
                    "strategy": "policy_active",
                    "specification_information": 0.0,
                    "expected_violation": 0.0,
                    "seed": int(seed),
                    "budget": budget,
                })
            for info_weight, violation_weight in weights:
                if info_weight < 0 or violation_weight < 0:
                    raise ValueError("Weights must be nonnegative")
                result = select_specification_aware_probes(
                    world.tool,
                    max(budgets),
                    pool,
                    random_state=int(seed),
                    specifications=world.specifications,
                    weights=SpecificationAcquisitionWeights(
                        specification_information=float(info_weight),
                        expected_violation=float(violation_weight),
                    ),
                )
                for budget in budgets:
                    evaluated = _evaluate(world, result.selected_states[:budget])
                    rows.append({
                        **evaluated,
                        "strategy": "specification_active",
                        "specification_information": float(info_weight),
                        "expected_violation": float(violation_weight),
                        "seed": int(seed),
                        "budget": budget,
                    })
    return rows
