from ipes_guard.benchmark_v2 import generate_benchmark_v2
from ipes_guard.domain import PolicyState
from ipes_guard.phase2_benchmark import phase2_probe_pool
from ipes_guard.policy_active import (
    ACQUISITION_ABLATIONS,
    FULL_ACQUISITION_WEIGHTS,
    acquisition_score,
    build_hypothesis_library,
    select_policy_active_probes,
)


def _test_tool():
    """Use a real reproducible Benchmark V2 tool as the test fixture."""
    tools, _ = generate_benchmark_v2(0)
    return tools[0]


def test_full_weights_preserve_default_acquisition_score() -> None:
    posterior = build_hypothesis_library()
    state = PolicyState(
        evidence_present=True,
        evidence_verified=False,
        resource_calls=4,
    )

    default_score = acquisition_score(state, posterior, [])
    explicit_score = acquisition_score(
        state,
        posterior,
        [],
        weights=FULL_ACQUISITION_WEIGHTS,
    )

    assert default_score == explicit_score


def test_all_ablation_variants_are_available() -> None:
    assert set(ACQUISITION_ABLATIONS) == {
        "policy_active_full",
        "policy_active_no_outcome",
        "policy_active_no_policy",
        "policy_active_no_boundary",
        "policy_active_no_novelty",
        "policy_active_outcome_only",
        "policy_active_policy_only",
    }


def test_all_variants_select_requested_number_of_probes() -> None:
    tool = _test_tool()
    pool = phase2_probe_pool()

    for weights in ACQUISITION_ABLATIONS.values():
        result = select_policy_active_probes(
            tool,
            budget=3,
            candidates=pool,
            random_state=7,
            weights=weights,
        )

        assert len(result.selected_states) == 3
        assert len(result.posterior_sizes) == 3
        assert len(result.acquisition_scores) == 3


def test_ablation_selection_is_reproducible() -> None:
    tool = _test_tool()
    pool = phase2_probe_pool()
    weights = ACQUISITION_ABLATIONS["policy_active_no_policy"]

    first = select_policy_active_probes(
        tool,
        budget=3,
        candidates=pool,
        random_state=11,
        weights=weights,
    )
    second = select_policy_active_probes(
        tool,
        budget=3,
        candidates=pool,
        random_state=11,
        weights=weights,
    )

    assert first.selected_states == second.selected_states
    assert first.posterior_sizes == second.posterior_sizes
    assert first.acquisition_scores == second.acquisition_scores
