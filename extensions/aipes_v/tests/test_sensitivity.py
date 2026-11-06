from aipes_v.sensitivity import run_weight_sensitivity


def test_zero_weights_match_original_policy_selector():
    rows = run_weight_sensitivity(weights=((0.0, 0.0),), seeds=(0,), budgets=(1, 2))
    for world in {r["world"] for r in rows}:
        for budget in (1, 2):
            matched = [
                r for r in rows
                if r["world"] == world and r["budget"] == budget
            ]
            assert len(matched) == 2
            assert matched[0]["violation_detected"] == matched[1]["violation_detected"]
            assert matched[0]["first_violation_probe"] == matched[1]["first_violation_probe"]


def test_sensitivity_has_matched_safe_and_unsafe_rows():
    rows = run_weight_sensitivity(
        weights=((0.0, 0.0), (2.0, 0.5)), seeds=(0,), budgets=(1,)
    )
    assert len(rows) == 12
    assert {r["unsafe_world"] for r in rows} == {True, False}
    assert all(not r["violation_detected"] for r in rows if not r["unsafe_world"])


def test_negative_weights_rejected():
    import pytest

    with pytest.raises(ValueError):
        run_weight_sensitivity(weights=((-1.0, 0.0),), seeds=(0,), budgets=(1,))
