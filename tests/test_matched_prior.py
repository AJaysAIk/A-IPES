import importlib.util
from pathlib import Path
import pandas as pd
import pytest
from ipes_guard.benchmark_v2 import generate_benchmark_v2, strategy_priors, prior_fingerprint, run_benchmark_v2

spec = importlib.util.spec_from_file_location("paired_mode_analysis", Path(__file__).parents[1]/"scripts/analyse_benchmark_v2.py")
analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis)


def test_full_priors_identical_for_every_tool():
    for seed in (0, 1, 2):
        tools, _ = generate_benchmark_v2(seed)
        for tool in tools:
            priors = strategy_priors(tool, "matched_full")
            assert priors["policy_active"] == priors["passive_characterisation"]
            assert prior_fingerprint(priors["policy_active"]) == prior_fingerprint(priors["passive_characterisation"])
            assert priors["policy_active"] == strategy_priors(tool)["policy_active"]


def test_legacy_retains_distinct_passive_prior():
    tools, _ = generate_benchmark_v2(0)
    assert any(strategy_priors(t)["policy_active"] != strategy_priors(t)["passive_characterisation"] for t in tools)


def test_fingerprint_ignores_order():
    tools, _ = generate_benchmark_v2(0)
    h = strategy_priors(tools[0])["policy_active"]
    assert prior_fingerprint(h) == prior_fingerprint(tuple(reversed(h)))


def frame():
    return pd.DataFrame([dict(budget=1, benchmark_seed=0, strategy=s, **{m: 0.5 for m in analysis.METRICS}) for s in ("policy_active", "passive_characterisation")])


@pytest.mark.parametrize("mode", ["legacy", "matched_full"])
def test_valid_explicit_mode(mode):
    f=frame(); f["prior_mode"]=mode; analysis.validate_pairs(f)


@pytest.mark.parametrize("values", [["legacy", "matched_full"], ["matched_full", None], ["bad", "bad"]])
def test_mixed_missing_unknown_modes_rejected(values):
    f=frame();f["prior_mode"]=values
    with pytest.raises(ValueError): analysis.validate_pairs(f)


def test_historical_file_without_mode_remains_valid():
    analysis.validate_pairs(frame())


def test_unknown_mode_rejected_before_running():
    with pytest.raises(ValueError): run_benchmark_v2(benchmark_seeds=(0,), budgets=(1,), prior_mode="unknown")


def test_fingerprint_changes_when_hypothesis_removed():
    tools, _ = generate_benchmark_v2(0)
    h = strategy_priors(tools[0])["policy_active"]

    assert len(h) > 1
    assert prior_fingerprint(h) != prior_fingerprint(h[:-1])
