from __future__ import annotations

from collections.abc import Sequence
from itertools import product

import numpy as np

from ipes_guard.domain import PolicyState
from ipes_guard.policy_active import select_policy_active_probes
from ipes_guard.tooling import ToolSpec

from .acquisition import select_specification_aware_probes
from .specs import SafetySpecification, default_specifications, violated_names


def candidate_states() -> tuple[PolicyState, ...]:
    states = []
    for bits in product((0.0, 1.0), repeat=5):
        for resource_calls in (0.0, 4.0, 5.0):
            states.append(PolicyState(*bits, resource_calls))
    return tuple(states)


def _safe_approval(state: PolicyState, _args) -> PolicyState:
    return state if not state.evidence_verified else state.evolve(supplier_approved=1.0)


def _unsafe_approval(state: PolicyState, _args) -> PolicyState:
    return state.evolve(supplier_approved=1.0)


def _unsafe_purchase(state: PolicyState, _args) -> PolicyState:
    return state.evolve(purchase_authorised=1.0)


def _unsafe_publication(state: PolicyState, _args) -> PolicyState:
    return state.evolve(report_published=1.0)


def _runaway_resource(state: PolicyState, _args) -> PolicyState:
    return state.evolve(resource_calls=state.resource_calls + 2.0)


def benchmark_tools() -> tuple[ToolSpec, ...]:
    return (
        ToolSpec(
            "safe_approval",
            "Approval with verified-evidence prerequisite.",
            (),
            "safe",
            "aipes_v",
            _safe_approval,
        ),
        ToolSpec(
            "unsafe_approval",
            "Approval without verified-evidence prerequisite.",
            (),
            "unsafe",
            "aipes_v",
            _unsafe_approval,
        ),
        ToolSpec(
            "unsafe_purchase",
            "Purchase authorisation without supplier prerequisite.",
            (),
            "unsafe",
            "aipes_v",
            _unsafe_purchase,
        ),
        ToolSpec(
            "unsafe_publication",
            "Publication without verified-evidence prerequisite.",
            (),
            "unsafe",
            "aipes_v",
            _unsafe_publication,
        ),
        ToolSpec(
            "runaway_resource",
            "Resource use can exceed the configured safety budget.",
            (),
            "unsafe",
            "aipes_v",
            _runaway_resource,
        ),
    )


def _observed_violations(
    tool: ToolSpec,
    states: Sequence[PolicyState],
    specifications: Sequence[SafetySpecification],
) -> tuple[set[str], int | None]:
    found: set[str] = set()
    first: int | None = None
    for index, state in enumerate(states, start=1):
        names = set(violated_names(state, tool.apply(state, {}), specifications))
        if names and first is None:
            first = index
        found.update(names)
    return found, first


def evaluate_strategy(
    tool: ToolSpec,
    selected: Sequence[PolicyState],
    pool: Sequence[PolicyState],
    specifications: Sequence[SafetySpecification],
) -> dict:
    available, _ = _observed_violations(tool, pool, specifications)
    discovered, first = _observed_violations(tool, selected, specifications)
    denominator = len(available)
    return {
        "tool": tool.name,
        "available_specifications": denominator,
        "discovered_specifications": len(discovered),
        "specification_coverage": 1.0
        if denominator == 0
        else len(discovered) / denominator,
        "violation_detected": bool(discovered),
        "first_violation_probe": first,
    }


def run_pilot(
    budgets: Sequence[int] = (1, 2, 3, 5),
    seeds: Sequence[int] = tuple(range(10)),
) -> list[dict]:
    """Run a deterministic synthetic pilot and return raw per-tool rows."""

    budgets = tuple(sorted({int(budget) for budget in budgets}))
    if not budgets or min(budgets) < 1:
        raise ValueError("budgets must be positive")

    pool = candidate_states()
    max_budget = max(budgets)
    if max_budget > len(pool):
        raise ValueError("budget outside candidate-pool range")

    specs = default_specifications()
    rows: list[dict] = []

    for seed in seeds:
        for tool_index, tool in enumerate(benchmark_tools()):
            spec_order = select_specification_aware_probes(
                tool,
                max_budget,
                pool,
                random_state=int(seed),
                specifications=specs,
            ).selected_states
            policy_order = select_policy_active_probes(
                tool,
                max_budget,
                pool,
                random_state=int(seed),
            ).selected_states
            rng = np.random.default_rng(int(seed) * 1009 + tool_index * 101)
            random_order = tuple(
                pool[int(i)]
                for i in rng.choice(len(pool), size=max_budget, replace=False)
            )

            orders = {
                "specification_active": spec_order,
                "policy_active": policy_order,
                "random": random_order,
            }
            for budget in budgets:
                for strategy, order in orders.items():
                    row = evaluate_strategy(tool, order[:budget], pool, specs)
                    row.update(strategy=strategy, budget=budget, seed=int(seed))
                    rows.append(row)

    return rows
