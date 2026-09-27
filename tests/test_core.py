from ipes_guard.domain import ActionContext, PolicyState
from ipes_guard.guard import IPESGuard
from ipes_guard.tooling import build_tool_catalogue, by_name


def test_renamed_approval_is_blocked_before_verification():
    tools = build_tool_catalogue()
    guard = IPESGuard()
    guard.characterise(tools)
    tool = by_name(tools)["confirm_vendor_eligibility"]

    state = PolicyState(evidence_present=1, evidence_verified=0)
    context = ActionContext(
        agent_role="compliance_agent",
        tool_name=tool.name,
        tool_description=tool.description,
        arguments={},
    )
    decision = guard.decide(state, context)

    assert not decision.allow
    assert decision.predicted_effect_class == "approve_supplier"
    assert any(v.code == "APPROVAL_WITHOUT_VERIFIED_EVIDENCE" for v in decision.violations)


def test_similar_benign_tool_is_allowed():
    tools = build_tool_catalogue()
    guard = IPESGuard()
    guard.characterise(tools)
    tool = by_name(tools)["preview_supplier_approval"]

    state = PolicyState(evidence_present=1, evidence_verified=0)
    context = ActionContext(
        agent_role="compliance_agent",
        tool_name=tool.name,
        tool_description=tool.description,
        arguments={},
    )
    decision = guard.decide(state, context)

    assert decision.allow
    assert decision.predicted_effect_class == "no_effect"


def test_active_probe_selector_returns_budgeted_model():
    from ipes_guard.active import select_active_probes

    tool = by_name(build_tool_catalogue())["confirm_vendor_eligibility"]
    result = select_active_probes(tool, budget=5)
    assert len(result.selected_states) == 5
    predicted = result.effect_model.predict(PolicyState(evidence_present=1, evidence_verified=0))
    assert predicted.supplier_approved == 1


def test_equal_budget_experiment_runs():
    from ipes_guard.budget_experiments import run_probe_budget_experiment

    summary, raw = run_probe_budget_experiment(budgets=(1, 2), seeds=(0,))
    assert not summary.empty
    assert not raw.empty
    assert set(summary["strategy"]) == {
        "single_default",
        "random",
        "fixed_boundary",
        "active",
    }
    assert set(summary["budget"]) == {1, 2}
