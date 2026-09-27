from __future__ import annotations

from dataclasses import asdict
from typing import Sequence

import numpy as np
import pandas as pd

from .benchmark_v2 import _summarise, generate_benchmark_v2
from .phase2_benchmark import (
    Phase2Model,
    _evaluate_tool_model,
    _passive_prior,
    _passive_states,
    _prefix_models,
    phase2_probe_pool,
)
from .policy_active import (
    ACQUISITION_ABLATIONS,
    build_hypothesis_library,
    select_policy_active_probes,
)


ABLATION_STRATEGIES = (
    "passive_characterisation",
    "policy_active_full",
    "policy_active_no_outcome",
    "policy_active_no_policy",
    "policy_active_no_boundary",
    "policy_active_no_novelty",
)


def run_acquisition_ablation(
    benchmark_seeds: Sequence[int] = tuple(range(30)),
    budgets: Sequence[int] = (2, 5),
    probe_seed: int = 0,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    """Evaluate A-IPES acquisition-component ablations.

    Every strategy receives the same generated benchmark world, candidate pool,
    probe budget and seeded tie-breaking configuration.
    """
    budgets = tuple(sorted(set(int(value) for value in budgets)))
    if not budgets:
        raise ValueError("At least one budget is required")
    if min(budgets) < 1:
        raise ValueError("Budgets must be positive")

    max_budget = max(budgets)
    pool = phase2_probe_pool()

    rows: list[dict] = []
    selections: list[dict] = []
    manifests: list[dict] = []

    for benchmark_seed in benchmark_seeds:
        tools, manifest = generate_benchmark_v2(int(benchmark_seed))
        manifests.append(asdict(manifest))

        for tool_index, tool in enumerate(tools):
            random_seed = (
                int(benchmark_seed) * 100_003
                + int(probe_seed) * 101
                + tool_index
            )

            orderings: dict[str, list] = {
                "passive_characterisation": _passive_states(pool, max_budget),
            }

            for strategy in ABLATION_STRATEGIES:
                if strategy == "passive_characterisation":
                    continue

                weights = ACQUISITION_ABLATIONS[strategy]
                result = select_policy_active_probes(
                    tool=tool,
                    budget=max_budget,
                    candidates=pool,
                    random_state=random_seed,
                    weights=weights,
                )
                orderings[strategy] = list(result.selected_states)

            priors = {
                strategy: (
                    _passive_prior(tool)
                    if strategy == "passive_characterisation"
                    else build_hypothesis_library()
                )
                for strategy in ABLATION_STRATEGIES
            }

            prefixes = {
                strategy: _prefix_models(
                    tool,
                    orderings[strategy],
                    budgets,
                    priors[strategy],
                )
                for strategy in ABLATION_STRATEGIES
            }

            for budget in budgets:
                for strategy in ABLATION_STRATEGIES:
                    model = prefixes[strategy][budget]
                    initial_count = len(priors[strategy])
                    final_count = len(model.hypotheses)

                    posterior_reduction = (
                        1.0 - final_count / max(1, initial_count)
                    )
                    information_gain = float(
                        np.log2(max(1, initial_count))
                        - np.log2(max(1, final_count))
                    )

                    fitted = Phase2Model(
                        strategy,
                        budget,
                        tool.name,
                        tuple(orderings[strategy][:budget]),
                        model,
                        final_count,
                    )

                    for selection_order, state in enumerate(
                        fitted.selected_states,
                        start=1,
                    ):
                        selections.append(
                            {
                                "benchmark_seed": benchmark_seed,
                                "probe_seed": random_seed,
                                "budget": budget,
                                "strategy": strategy,
                                "tool_name": tool.name,
                                "selection_order": selection_order,
                                **state.as_dict(),
                            }
                        )

                    for row in _evaluate_tool_model(tool, fitted):
                        row.update(
                            {
                                "benchmark_seed": benchmark_seed,
                                "probe_seed": random_seed,
                                "initial_hypothesis_count": initial_count,
                                "posterior_reduction_ratio": posterior_reduction,
                                "information_gain_bits": information_gain,
                            }
                        )
                        rows.append(row)

    raw = pd.DataFrame(rows)
    selected = pd.DataFrame(selections)
    manifest_df = pd.DataFrame(manifests)

    per_benchmark = (
        raw.groupby(
            ["benchmark_seed", "budget", "strategy"],
            sort=False,
        )
        .apply(_summarise, include_groups=False)
        .reset_index()
    )

    mean_metrics = [
        "attack_recall",
        "false_positive_rate",
        "precision",
        "f1",
        "balanced_accuracy",
        "policy_exact_match",
        "effect_mae",
        "shifted_attack_recall",
        "posterior_reduction_ratio",
        "information_gain_bits",
    ]

    std_metrics = [
        "attack_recall",
        "false_positive_rate",
        "policy_exact_match",
        "effect_mae",
    ]

    summary = (
        per_benchmark.groupby(["budget", "strategy"], sort=False)
        .agg(
            **{
                f"{metric}_mean": (metric, "mean")
                for metric in mean_metrics
            },
            **{
                f"{metric}_std": (metric, "std")
                for metric in std_metrics
            },
        )
        .reset_index()
    )

    return summary, per_benchmark, raw, selected, manifest_df
