from ipes_guard.benchmark_v2 import generate_benchmark_v2, run_benchmark_v2


def test_generation_is_reproducible_and_seed_sensitive():
    tools_a, manifest_a = generate_benchmark_v2(7)
    tools_b, manifest_b = generate_benchmark_v2(7)
    _, manifest_c = generate_benchmark_v2(8)
    assert manifest_a == manifest_b
    assert [tool.name for tool in tools_a] == [tool.name for tool in tools_b]
    assert manifest_a != manifest_c


def test_benchmark_v2_reports_independent_replicates():
    summary, per_benchmark, raw, selected, manifests = run_benchmark_v2(
        benchmark_seeds=(0, 1), budgets=(1, 2), probe_seed=0
    )
    assert set(manifests["benchmark_seed"]) == {0, 1}
    assert set(per_benchmark["benchmark_seed"]) == {0, 1}
    assert set(summary["strategy"]) == {
        "single_default", "passive_characterisation", "random", "fixed_boundary", "policy_active"
    }
    assert "posterior_reduction_ratio" in per_benchmark.columns
    assert "information_gain_bits" in per_benchmark.columns
    assert not raw.empty
    assert not selected.empty
