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
class VerificationWorld:
    name: str
    tool: ToolSpec
    specifications: tuple[SafetySpecification, ...]
    unsafe: bool


def candidate_states() -> tuple[PolicyState, ...]:
    """Matched pool with zero initial resource use."""

    return tuple(PolicyState(*bits, 0.0) for bits in product((0.0, 1.0), repeat=5))


def _contextual_burst_spec(
    name: str,
    description: str,
    context: Callable[[PolicyState], bool],
) -> SafetySpecification:
    return SafetySpecification(
        name,
        description,
        lambda before, after: bool(
            context(before) and (after.resource_calls - before.resource_calls) > 1.0
        ),
    )


def post_publication_specification() -> tuple[SafetySpecification, ...]:
    return (
        _contextual_burst_spec(
            "post_publication_resource_burst",
            "After publication, one transition must not consume more than one resource call.",
            lambda state: bool(state.report_published),
        ),
    )


def post_authorisation_specification() -> tuple[SafetySpecification, ...]:
    return (
        _contextual_burst_spec(
            "post_authorisation_resource_burst",
            "After purchase authorisation, one transition must not consume more than one resource call.",
            lambda state: bool(state.purchase_authorised),
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
        "Context-dependent resource transition used by the A-IPES-V v0.2 pilot.",
        (),
        "contextual_resource",
        "aipes_v_v02",
        apply,
    )


def verification_worlds() -> tuple[VerificationWorld, ...]:
    published = lambda state: bool(state.report_published)
    authorised = lambda state: bool(state.purchase_authorised)
    return (
        VerificationWorld(
            "publication_safe",
            _resource_tool("publication_bounded", published, 1.0),
            post_publication_specification(),
            False,
        ),
        VerificationWorld(
            "publication_burst",
            _resource_tool("publication_burst", published, 2.0),
            post_publication_specification(),
            True,
        ),
        VerificationWorld(
            "authorisation_safe",
            _resource_tool("authorisation_bounded", authorised, 1.0),
            post_authorisation_specification(),
            False,
        ),
        VerificationWorld(
            "authorisation_burst",
            _resource_tool("authorisation_burst", authorised, 2.0),
            post_authorisation_specification(),
            True,
        ),
    )


V02_WEIGHTS = SpecificationAcquisitionWeights(
    specification_information=2.0,
    expected_violation=0.5,
)


def _evaluate(
    world: VerificationWorld,
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


def run_nonredundant_pilot(
    budgets: Sequence[int] = (1, 2, 3, 5),
    seeds: Sequence[int] = tuple(range(10)),
) -> list[dict]:
    """Paired v0.2 pilot with one max-budget trajectory per strategy."""

    budgets = tuple(sorted(set(int(b) for b in budgets)))
    if not budgets or min(budgets) < 1:
        raise ValueError("budgets must be positive")
    pool = candidate_states()
    if max(budgets) > len(pool):
        raise ValueError("budget exceeds candidate-pool size")

    rows: list[dict] = []
    max_budget = max(budgets)

    for seed in seeds:
        for world_index, world in enumerate(verification_worlds()):
            specification_result = select_specification_aware_probes(
                world.tool,
                max_budget,
                pool,
                random_state=int(seed),
                specifications=world.specifications,
                weights=V02_WEIGHTS,
            )
            policy_result = select_policy_active_probes(
                world.tool,
                max_budget,
                pool,
                random_state=int(seed),
            )
            rng = np.random.default_rng(int(seed) * 1009 + world_index * 101)
            random_order = tuple(
                pool[int(i)]
                for i in rng.choice(len(pool), size=max_budget, replace=False)
            )

            orders = {
                "specification_active": specification_result.selected_states,
                "policy_active": policy_result.selected_states,
                "random": random_order,
            }
            for budget in budgets:
                for strategy, order in orders.items():
                    row = _evaluate(world, order[:budget])
                    row.update(
                        strategy=strategy,
                        budget=budget,
                        seed=int(seed),
                    )
                    rows.append(row)

    return rows
