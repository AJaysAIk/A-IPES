from aipes_v.nonredundant import (
    V02_WEIGHTS,
    candidate_states,
    post_publication_specification,
    run_nonredundant_pilot,
    verification_worlds,
)
from aipes_v.specs import violated_names

from ipes_guard.domain import PolicyState


def test_contextual_specification_is_nonredundant_with_total_resource_threshold():
    spec = post_publication_specification()
    before = PolicyState(report_published=1, resource_calls=0)
    after = before.evolve(resource_calls=2)
    assert violated_names(before, after, spec) == ("post_publication_resource_burst",)
    assert after.resource_calls <= 5


def test_candidate_pool_removes_total_resource_threshold_proxy():
    pool = candidate_states()
    assert len(pool) == 32
    assert all(state.resource_calls == 0 for state in pool)


def test_worlds_include_safe_and_unsafe_matched_contexts():
    worlds = verification_worlds()
    assert {world.unsafe for world in worlds} == {False, True}
    assert len(worlds) == 4


def test_v02_weights_make_specification_information_primary_extension_signal():
    assert V02_WEIGHTS.specification_information == 2.0
    assert V02_WEIGHTS.expected_violation == 0.5


def test_budget_one_exposes_incremental_value_on_contextual_burst_worlds():
    rows = run_nonredundant_pilot(budgets=(1,), seeds=(0,))
    unsafe = [row for row in rows if row["unsafe_world"]]
    spec = [row for row in unsafe if row["strategy"] == "specification_active"]
    policy = [row for row in unsafe if row["strategy"] == "policy_active"]
    assert all(row["violation_detected"] for row in spec)
    assert not any(row["violation_detected"] for row in policy)


def test_safe_worlds_have_no_monitor_false_alarms():
    rows = run_nonredundant_pilot(budgets=(1, 2), seeds=(0,))
    safe = [row for row in rows if not row["unsafe_world"]]
    assert safe
    assert not any(row["violation_detected"] for row in safe)
