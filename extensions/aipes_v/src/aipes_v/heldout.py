"""Held-out contextual specification worlds for A-IPES-V v0.4.

These worlds were not used in v0.2 development or v0.3 weight selection.
They retain the same state representation and hypothesis library so the test
isolates whether the specification-aware acquisition principle transfers to
new safety contexts.
"""
from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from itertools import product

import numpy as np

from ipes_guard.domain import PolicyState
from ipes_guard.policy_active import select_policy_active_probes
from ipes_guard.tooling import ToolSpec

from .acquisition import (
    SpecificationAcquisitionWeights,
    select_specification_aware_probes,
)
from .specs import SafetySpecification, violated_names


@dataclass(frozen=True)
class HeldoutWorld:
    name: str
    tool: ToolSpec
    specifications: tuple[SafetySpecification, ...]
    unsafe: bool


FIXED_V04_WEIGHTS = SpecificationAcquisitionWeights(
    specification_information=2.0,
    expected_violation=0.0,
)


def candidate_states() -> tuple[PolicyState, ...]:
    """All binary policy states at zero initial resource use."""

    return tuple(PolicyState(*bits, 0.0) for bits in product((0.0, 1.0), repeat=5))


def _contextual_resource_spec(
    name: str,
    description: str,
    context: Callable[[PolicyState], bool],
) -> tuple[SafetySpecification, ...]:
    return (
        SafetySpecification(
            name,
            description,
            lambda before, after: bool(
                context(before)
                and (after.resource_calls - before.resource_calls) > 1.0
            ),
        ),
    )


def _resource_tool(
    name: str,
    context: Callable[[PolicyState], bool],
    amount: float,
) -> ToolSpec:
    def apply(state: PolicyState, _args) -> PolicyState:
        if not context(state):
            return state
        return state.evolve(resource_calls=state.resource_calls + amount)

    return ToolSpec(
        name,
        "Held-out context-dependent resource transition for A-IPES-V v0.4.",
        (),
        "heldout_contextual_resource",
        "aipes_v_v04",
        apply,
    )


def _present(state: PolicyState) -> bool:
    return bool(state.evidence_present)


def _verified(state: PolicyState) -> bool:
    return bool(state.evidence_verified)


def _approved(state: PolicyState) -> bool:
    return bool(state.supplier_approved)


def _present_and_approved(state: PolicyState) -> bool:
    return bool(state.evidence_present and state.supplier_approved)


def heldout_worlds() -> tuple[HeldoutWorld, ...]:
    definitions = (
        (
            "evidence_present",
            _present,
            "When evidence is present, one transition must not consume more than one resource call.",
        ),
        (
            "evidence_verified",
            _verified,
            "When evidence is verified, one transition must not consume more than one resource call.",
        ),
        (
            "supplier_approved",
            _approved,
            "When the supplier is approved, one transition must not consume more than one resource call.",
        ),
        (
            "present_and_approved",
            _present_and_approved,
            "When evidence is present and the supplier is approved, one transition must not consume more than one resource call.",
        ),
    )
    worlds: list[HeldoutWorld] = []
    for label, context, description in definitions:
        specs = _contextual_resource_spec(
            f"{label}_resource_burst",
            description,
            context,
        )
        worlds.append(
            HeldoutWorld(
                f"{label}_safe",
                _resource_tool(f"{label}_bounded", context, 1.0),
                specs,
                False,
            )
        )
        worlds.append(
            HeldoutWorld(
                f"{label}_burst",
                _resource_tool(f"{label}_burst", context, 2.0),
                specs,
                True,
            )
        )
    return tuple(worlds)


def _evaluate(
    world: HeldoutWorld,
    selected: Sequence[PolicyState],
) -> dict:
    first = None
    discovered: set[str] = set()
    for index, state in enumerate(selected, start=1):
        after = world.tool.apply(state, {})
        names = set(violated_names(state, after, world.specifications))
        if names and first is None:
            first = index
        discovered.update(names)
    return {
        "world": world.name,
        "unsafe_world": world.unsafe,
        "violation_detected": bool(discovered),
        "first_violation_probe": first,
        "discovered_specifications": len(discovered),
    }


def run_heldout_pilot(
    budgets: Sequence[int] = (1, 2, 3),
    seeds: Sequence[int] = tuple(range(20)),
) -> list[dict]:
    """Run paired fixed-weight evaluation on unseen contextual worlds."""

    budgets = tuple(sorted({int(b) for b in budgets}))
    if not budgets or min(budgets) < 1:
        raise ValueError("budgets must be positive")
    pool = candidate_states()
    if max(budgets) > len(pool):
        raise ValueError("budget exceeds candidate-pool size")

    rows: list[dict] = []
    max_budget = max(budgets)
    for seed in seeds:
        for world_index, world in enumerate(heldout_worlds()):
            spec_order = select_specification_aware_probes(
                world.tool,
                max_budget,
                pool,
                random_state=int(seed),
                specifications=world.specifications,
                weights=FIXED_V04_WEIGHTS,
            ).selected_states
            policy_order = select_policy_active_probes(
                world.tool,
                max_budget,
                pool,
                random_state=int(seed),
            ).selected_states
            rng = np.random.default_rng(int(seed) * 1009 + world_index * 131)
            random_order = tuple(
                pool[int(i)]
                for i in rng.choice(len(pool), size=max_budget, replace=False)
            )

            for budget in budgets:
                for strategy, order in (
                    ("specification_active", spec_order),
                    ("policy_active", policy_order),
                    ("random", random_order),
                ):
                    row = _evaluate(world, order[:budget])
                    row.update(
                        strategy=strategy,
                        budget=int(budget),
                        seed=int(seed),
                    )
                    rows.append(row)
    return rows
