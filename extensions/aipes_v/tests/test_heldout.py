from aipes_v.heldout import (
    FIXED_V04_WEIGHTS,
    candidate_states,
    heldout_worlds,
    run_heldout_pilot,
)


def test_v04_weights_are_fixed_before_heldout_results():
    assert FIXED_V04_WEIGHTS.specification_information == 2.0
    assert FIXED_V04_WEIGHTS.expected_violation == 0.0


def test_heldout_worlds_are_new_context_families():
    names = {world.name for world in heldout_worlds()}
    assert len(names) == 8
    assert all("publication" not in name for name in names)
    assert all("authorisation" not in name for name in names)


def test_heldout_candidate_pool_starts_at_zero_resource_use():
    pool = candidate_states()
    assert len(pool) == 32
    assert all(state.resource_calls == 0.0 for state in pool)


def test_heldout_safe_controls_do_not_alarm():
    rows = run_heldout_pilot(budgets=(1, 2), seeds=(0,))
    safe = [row for row in rows if not row["unsafe_world"]]
    assert safe
    assert all(not row["violation_detected"] for row in safe)


def test_heldout_runner_emits_matched_strategies():
    rows = run_heldout_pilot(budgets=(1,), seeds=(0,))
    assert {row["strategy"] for row in rows} == {
        "specification_active",
        "policy_active",
        "random",
    }
