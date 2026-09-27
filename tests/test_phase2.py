from ipes_guard.domain import PolicyState
from ipes_guard.phase2_benchmark import (
    build_phase2_tool_catalogue,
    fit_phase2_model,
    run_phase2_policy_probe_experiment,
)
from ipes_guard.tooling import by_name


def test_policy_active_finds_conditional_approval_effect():
    tool = by_name(build_phase2_tool_catalogue())["archive_vendor_assessment"]
    fitted = fit_phase2_model(tool, "policy_active", budget=5, seed=0)
    unsafe_state = PolicyState(evidence_present=1, evidence_verified=0, resource_calls=4)
    predicted = fitted.model.predict(unsafe_state)
    assert predicted.supplier_approved == 1


def test_phase2_uses_disjoint_probe_and_evaluation_resources():
    from ipes_guard.phase2_benchmark import phase2_evaluation_pool, phase2_probe_pool

    probe_resources = {state.resource_calls for state in phase2_probe_pool()}
    evaluation_resources = {state.resource_calls for state in phase2_evaluation_pool()}
    assert probe_resources.isdisjoint(evaluation_resources)


def test_phase2_benchmark_runs_and_reports_policy_metrics():
    tools = build_phase2_tool_catalogue()[:4]
    summary, raw, selected = run_phase2_policy_probe_experiment(
        budgets=(1, 3), seeds=(0,), tools=tools
    )
    assert not summary.empty
    assert not raw.empty
    assert not selected.empty
    assert set(summary["strategy"]) == {
        "single_default",
        "passive_characterisation",
        "random",
        "fixed_boundary",
        "policy_active",
    }
    assert "policy_exact_match_mean" in summary.columns
    assert "balanced_accuracy_mean" in summary.columns


def test_passive_characterisation_is_nonadaptive_and_budgeted():
    tool = by_name(build_phase2_tool_catalogue())["archive_vendor_assessment"]
    first = fit_phase2_model(tool, "passive_characterisation", budget=3, seed=0)
    second = fit_phase2_model(tool, "passive_characterisation", budget=3, seed=99)
    assert len(first.selected_states) == 3
    assert first.selected_states == second.selected_states
    assert first.posterior_size > 0
