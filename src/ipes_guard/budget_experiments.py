from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Sequence

import numpy as np
import pandas as pd

from .active import candidate_policy_states, select_active_probes
from .domain import ActionContext, PolicyState
from .experiments import build_scenarios
from .policy import evaluate_transition, infer_effect_class
from .probes import canonical_probe_states
from .signature import EffectModel, fit_effect_model
from .tooling import ToolSpec, build_tool_catalogue, by_name


@dataclass(frozen=True)
class StrategyModel:
    strategy: str
    budget: int
    tool_name: str
    selected_states: tuple[PolicyState, ...]
    model: EffectModel


def _boundary_score(state: PolicyState) -> float:
    score = 0.0
    if state.evidence_present and not state.evidence_verified:
        score += 1.0
    if state.evidence_verified and not state.supplier_approved:
        score += 1.0
    if state.supplier_approved and not state.purchase_authorised:
        score += 1.0
    if state.resource_calls == 5:
        score += 1.0
    return score


def _fixed_boundary_states(budget: int) -> list[PolicyState]:
    pool = candidate_policy_states()
    ordered = sorted(
        pool,
        key=lambda s: (
            -_boundary_score(s),
            tuple(s.to_vector().tolist()),
        ),
    )
    return ordered[:budget]


def _random_states(budget: int, random_state: int) -> list[PolicyState]:
    pool = candidate_policy_states()
    rng = np.random.default_rng(random_state)
    idx = rng.choice(len(pool), size=budget, replace=False)
    return [pool[int(i)] for i in idx]


def fit_strategy_model(
    tool: ToolSpec,
    strategy: str,
    budget: int,
    random_state: int,
) -> StrategyModel:
    if strategy == "single_default":
        states = [PolicyState()]
        model = fit_effect_model(tool, states)
    elif strategy == "random":
        states = _random_states(budget, random_state)
        model = fit_effect_model(tool, states)
    elif strategy == "fixed_boundary":
        states = _fixed_boundary_states(budget)
        model = fit_effect_model(tool, states)
    elif strategy == "active":
        result = select_active_probes(
            tool,
            budget=budget,
            random_state=random_state,
        )
        states = list(result.selected_states)
        model = result.effect_model
    else:
        raise ValueError(f"Unknown strategy: {strategy}")
    return StrategyModel(strategy, budget, tool.name, tuple(states), model)


def _predict_unsafe(
    strategy_model: StrategyModel,
    state: PolicyState,
    context: ActionContext,
) -> tuple[bool, str]:
    after = strategy_model.model.predict(state)
    effect = infer_effect_class(state, after)
    violations = evaluate_transition(state, after, context, effect)
    return bool(violations), effect


def _effect_error(tool: ToolSpec, model: EffectModel, states: Sequence[PolicyState]) -> float:
    errors = []
    for state in states:
        expected = tool.apply(state, {}).to_vector()
        predicted = model.predict(state).to_vector()
        errors.append(float(np.mean(np.abs(expected - predicted))))
    return float(np.mean(errors)) if errors else 0.0


def run_probe_budget_experiment(
    budgets: Sequence[int] = (1, 2, 3, 5, 8, 10),
    seeds: Sequence[int] = (0, 1, 2, 3, 4),
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compare equal-budget probe strategies.

    Important: this is still a controlled synthetic benchmark. Seeds quantify
    strategy/model variability; they are not treated as independent scenarios.
    """
    tools = build_tool_catalogue()
    tool_lookup = by_name(tools)
    scenarios = build_scenarios(tools)
    evaluation_states = candidate_policy_states()

    rows: List[dict] = []
    strategies = ("single_default", "random", "fixed_boundary", "active")

    for budget in budgets:
        for seed in seeds:
            fitted: Dict[tuple[str, str], StrategyModel] = {}
            for strategy in strategies:
                effective_budget = 1 if strategy == "single_default" else budget
                for tool in tools:
                    fitted[(strategy, tool.name)] = fit_strategy_model(
                        tool,
                        strategy=strategy,
                        budget=effective_budget,
                        random_state=seed,
                    )

            for scenario in scenarios:
                tool = tool_lookup[scenario.tool_name]
                context = ActionContext(
                    agent_role=scenario.agent_role,
                    tool_name=tool.name,
                    tool_description=tool.description,
                    arguments=scenario.arguments,
                )
                for strategy in strategies:
                    model = fitted[(strategy, tool.name)]
                    predicted_unsafe, effect = _predict_unsafe(
                        model,
                        scenario.initial_state,
                        context,
                    )
                    rows.append(
                        {
                            "budget": budget,
                            "seed": seed,
                            "strategy": strategy,
                            "scenario_id": scenario.scenario_id,
                            "tool_name": scenario.tool_name,
                            "mutation_type": scenario.mutation_type,
                            "unsafe": scenario.unsafe,
                            "predicted_unsafe": predicted_unsafe,
                            "correct": predicted_unsafe == scenario.unsafe,
                            "predicted_effect_class": effect,
                            "effect_mae": _effect_error(
                                tool,
                                model.model,
                                evaluation_states,
                            ),
                        }
                    )

    raw = pd.DataFrame(rows)

    def summarise(group: pd.DataFrame) -> pd.Series:
        unsafe = group[group["unsafe"]]
        safe = group[~group["unsafe"]]
        tp = int(unsafe["predicted_unsafe"].sum())
        fn = int((~unsafe["predicted_unsafe"]).sum())
        fp = int(safe["predicted_unsafe"].sum())
        tn = int((~safe["predicted_unsafe"]).sum())
        base = group[group["mutation_type"].isin(["base", "similar_benign"])]
        shifted = group[~group["mutation_type"].isin(["base", "similar_benign"])]
        base_unsafe = base[base["unsafe"]]
        shifted_unsafe = shifted[shifted["unsafe"]]
        base_recall = float(base_unsafe["predicted_unsafe"].mean()) if len(base_unsafe) else np.nan
        shifted_recall = float(shifted_unsafe["predicted_unsafe"].mean()) if len(shifted_unsafe) else np.nan
        return pd.Series(
            {
                "n": len(group),
                "attack_recall": tp / max(1, tp + fn),
                "false_positive_rate": fp / max(1, fp + tn),
                "accuracy": (tp + tn) / max(1, len(group)),
                "effect_mae": float(group["effect_mae"].mean()),
                "base_attack_recall": base_recall,
                "shifted_attack_recall": shifted_recall,
                "mutation_gap": base_recall - shifted_recall,
                "tp": tp,
                "fn": fn,
                "fp": fp,
                "tn": tn,
            }
        )

    per_seed = (
        raw.groupby(["budget", "seed", "strategy"], sort=False)
        .apply(summarise, include_groups=False)
        .reset_index()
    )

    summary = (
        per_seed.groupby(["budget", "strategy"], sort=False)
        .agg(
            attack_recall_mean=("attack_recall", "mean"),
            attack_recall_std=("attack_recall", "std"),
            false_positive_rate_mean=("false_positive_rate", "mean"),
            effect_mae_mean=("effect_mae", "mean"),
            mutation_gap_mean=("mutation_gap", "mean"),
            shifted_attack_recall_mean=("shifted_attack_recall", "mean"),
        )
        .reset_index()
    )
    return summary, raw
