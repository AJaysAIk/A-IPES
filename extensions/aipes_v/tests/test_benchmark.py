from aipes_v.benchmark import benchmark_tools, candidate_states, run_pilot


def test_candidate_pool_is_nonempty_and_unique():
    pool = candidate_states()
    assert len(pool) == 96
    assert len(set(pool)) == len(pool)


def test_pilot_produces_bounded_metrics_for_all_strategies():
    rows = run_pilot(budgets=(1, 2), seeds=(0,))
    assert rows
    assert {row["strategy"] for row in rows} == {"specification_active", "policy_active", "random"}
    assert {row["tool"] for row in rows} == {tool.name for tool in benchmark_tools()}
    assert all(0.0 <= row["specification_coverage"] <= 1.0 for row in rows)


def test_safe_tool_has_no_available_violations():
    rows = run_pilot(budgets=(1,), seeds=(0,))
    safe = [row for row in rows if row["tool"] == "safe_approval"]
    assert safe
    assert all(row["available_specifications"] == 0 for row in safe)
    assert all(row["specification_coverage"] == 1.0 for row in safe)
