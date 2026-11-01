import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from ipes_guard.domain import PolicyState
from ipes_guard.tooling import ToolSpec
from ipes_guard.policy_active import (Trigger, TransitionHypothesis, VersionSpaceEffectModel,
    fit_version_space_model, select_policy_active_probes)
from ipes_guard.phase2_benchmark import _prefix_models


def tool(fn):
    return ToolSpec("test", "test", (), "no_effect", "base", fn)


def test_true_no_effect_is_not_inconsistency():
    h = TransitionHypothesis(None, 0.0, Trigger(()))
    model = fit_version_space_model(tool(lambda s, a: s), [PolicyState()], [h])
    assert model.identification_status == "consistent"
    assert model.consistent_hypothesis_count == 1
    assert not model.fallback_used


def test_ambiguity_is_distinct_from_identification():
    model = VersionSpaceEffectModel("test", (
        TransitionHypothesis(None, 0.0, Trigger(())),
        TransitionHypothesis(0, 1.0, Trigger(()))))
    assert model.identification_status == "ambiguous"


def test_unmodelled_transition_exposes_legacy_fallback():
    bad = tool(lambda s, a: s.evolve(resource_calls=99))
    model = fit_version_space_model(bad, [PolicyState()])
    assert model.identification_status == "inconsistent"
    assert model.consistent_hypothesis_count == 0
    assert model.fallback_used
    assert model.predict(PolicyState()) == PolicyState()  # compatibility only


def test_contradictory_repeat_never_becomes_identified():
    calls = []
    def alternating(s, a):
        calls.append(1)
        return s if len(calls) == 1 else s.evolve(evidence_present=1)
    model = fit_version_space_model(tool(alternating), [PolicyState(), PolicyState()])
    assert model.identification_status == "inconsistent"
    assert model.consistent_hypothesis_count == 0


def test_prefix_keeps_empty_prior_visible_after_fallback():
    bad = tool(lambda s, a: s.evolve(resource_calls=99))
    models = _prefix_models(bad, [PolicyState(), PolicyState(evidence_present=1)], [1, 2])
    assert all(m.identification_status == "inconsistent" for m in models.values())
    assert all(m.fallback_used for m in models.values())


def test_active_trace_records_real_counts_and_observation():
    bad = tool(lambda s, a: s.evolve(resource_calls=99))
    result = select_policy_active_probes(bad, 2, [PolicyState(), PolicyState(evidence_present=1)])
    assert result.model.identification_status == "inconsistent"
    assert [d["consistent_count_after"] for d in result.diagnostics] == [0, 0]
    assert all(d["after"]["resource_calls"] == 99 for d in result.diagnostics)
    assert len(result.diagnostics) == 2


spec = importlib.util.spec_from_file_location("paired_analysis", Path(__file__).parents[1] / "scripts/analyse_benchmark_v2.py")
analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis)


def pairs():
    return pd.DataFrame([dict(budget=1, benchmark_seed=seed, strategy=strategy,
         **{m: 0.5 for m in analysis.METRICS})
         for seed in [0, 1] for strategy in ["policy_active", "passive_characterisation"]])


def test_valid_pairs():
    analysis.validate_pairs(pairs())


@pytest.mark.parametrize("kind", ["duplicate", "missing", "nan", "empty"])
def test_invalid_pairs_rejected(kind):
    frame = pairs()
    if kind == "duplicate": frame = pd.concat([frame, frame.iloc[[0]]])
    elif kind == "missing": frame = frame.iloc[1:]
    elif kind == "nan": frame.loc[0, "attack_recall"] = np.nan
    else: frame = frame.iloc[:0]
    with pytest.raises(ValueError): analysis.validate_pairs(frame)
