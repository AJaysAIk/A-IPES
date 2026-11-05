from aipes_v.acquisition import (
    select_specification_aware_probes,
    specification_information_score,
)

from ipes_guard.domain import PolicyState
from ipes_guard.policy_active import TransitionHypothesis, Trigger
from ipes_guard.tooling import ToolSpec


def test_specification_information_is_positive_when_hypotheses_disagree_on_safety():
    state = PolicyState(evidence_verified=0, supplier_approved=0)
    posterior = (
        TransitionHypothesis(None, 0.0, Trigger(())),
        TransitionHypothesis(2, 1.0, Trigger(())),
    )
    assert specification_information_score(state, posterior) > 0


def test_specification_selector_records_observed_violations():
    tool = ToolSpec(
        "unsafe_approval",
        "unsafe",
        (),
        "unsafe",
        "test",
        lambda state, args: state.evolve(supplier_approved=1.0),
    )
    candidates = (
        PolicyState(evidence_verified=0),
        PolicyState(evidence_verified=1),
        PolicyState(evidence_verified=0, evidence_present=1),
    )
    result = select_specification_aware_probes(tool, 2, candidates, random_state=7)
    assert len(result.selected_states) == 2
    assert len(result.diagnostics) == 2
    assert any(d["observed_violations"] for d in result.diagnostics)
