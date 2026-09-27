from ipes_guard.acquisition_ablation import (
    ABLATION_STRATEGIES,
    run_acquisition_ablation,
)


def test_ablation_runner_returns_expected_strategies() -> None:
    summary, per_benchmark, raw, selected, manifests = (
        run_acquisition_ablation(
            benchmark_seeds=(0,),
            budgets=(2,),
            probe_seed=0,
        )
    )

    assert set(summary["strategy"]) == set(ABLATION_STRATEGIES)
    assert set(per_benchmark["strategy"]) == set(ABLATION_STRATEGIES)
    assert set(raw["strategy"]) == set(ABLATION_STRATEGIES)
    assert set(selected["strategy"]) == set(ABLATION_STRATEGIES)

    assert set(summary["budget"]) == {2}
    assert set(per_benchmark["benchmark_seed"]) == {0}
    assert set(manifests["benchmark_seed"]) == {0}


def test_ablation_runner_is_reproducible() -> None:
    first = run_acquisition_ablation(
        benchmark_seeds=(0,),
        budgets=(2,),
        probe_seed=3,
    )
    second = run_acquisition_ablation(
        benchmark_seeds=(0,),
        budgets=(2,),
        probe_seed=3,
    )

    first_summary, first_per_benchmark, _, first_selected, _ = first
    second_summary, second_per_benchmark, _, second_selected, _ = second

    assert first_summary.equals(second_summary)
    assert first_per_benchmark.equals(second_per_benchmark)
    assert first_selected.equals(second_selected)


def test_full_ablation_matches_existing_full_selector_name() -> None:
    summary, _, _, _, _ = run_acquisition_ablation(
        benchmark_seeds=(0,),
        budgets=(2, 5),
    )

    assert "policy_active_full" in set(summary["strategy"])
    assert set(summary["budget"]) == {2, 5}
