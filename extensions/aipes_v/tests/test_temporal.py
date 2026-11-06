import pytest
from aipes_v.temporal import (
    TemporalModel,
    candidate_traces,
    library,
    monitor,
    refine,
    run_temporal,
    select_trace,
)


def test_temporal_monitor_and_mutants():
    safe = TemporalModel(False, False, False)
    early = TemporalModel(True, False, False)
    stale = TemporalModel(False, True, False)
    for trace in (("grant", "use"), ("grant", "revoke", "grant", "use")):
        assert not monitor(trace, safe.execute(trace))
    assert monitor(("use",), early.execute(("use",)))
    trace = ("grant", "revoke", "use")
    assert monitor(trace, stale.execute(trace))
    assert not monitor(trace, safe.execute(trace))
    assert not monitor(("use",), stale.execute(("use",)))
    assert not monitor(trace, early.execute(trace))
    # The same public trace is judged solely by its observed acceptance.
    assert monitor(trace, ((False, False), (False, False), (True, False)))
    with pytest.raises(ValueError):
        monitor(trace, ())


def test_exhaustive_labels_and_minimum_stale_depth():
    for model in library():
        assert any(monitor(t, model.execute(t)) for t in candidate_traces()) == (
            model.early or model.stale
        )
    stale = TemporalModel(False, True, False)
    assert all(not monitor(t[:2], stale.execute(t[:2])) for t in candidate_traces())


def test_refinement_uses_full_response_and_rejects_misspecification():
    trace = ("idle", "use", "grant", "use")
    world = TemporalModel(False, False, True)
    posterior = refine(library(), trace, world.execute(trace))
    assert world in posterior
    assert all(m.pulse and not m.early for m in posterior)
    with pytest.raises(ValueError):
        refine(library(), ("grant",), ((True, True),))


def test_ceg_proposes_and_validates_a_spurious_counterexample():
    models, pool = library(), candidate_traces()
    predictions = {(m, t): m.execute(t) for m in models for t in pool}
    violations = {(m, t): monitor(t, predictions[m, t]) for m in models for t in pool}
    trace = select_trace("counterexample_guided", pool, models, predictions, violations)
    assert any(violations[m, trace] for m in models)
    safe = models[0]
    response = safe.execute(trace)
    assert not monitor(trace, response)
    remaining = refine(models, trace, response)
    assert len(remaining) < len(models)
    assert all(not violations[m, trace] for m in remaining)


def test_reproducibility_prefixes_and_call_accounting():
    rows, audits = run_temporal(budgets=(1, 2, 4), seeds=(0,))
    assert (rows, audits) == run_temporal(budgets=(1, 2, 4), seeds=(0,))
    short_rows, short_audits = run_temporal(budgets=(1, 2), seeds=(0,))
    assert short_rows == [r for r in rows if r["budget"] <= 2]
    assert short_audits == [r for r in audits if r["query"] <= 2]
    assert all(r["action_calls"] == 4 * r["query"] for r in audits)
    assert all(r["resets"] == r["query"] for r in audits)
    assert all(not r["violation_detected"] for r in rows if not r["unsafe_world"])
    for world in library():
        for strategy in {r["strategy"] for r in rows}:
            selected = [
                r["trace"]
                for r in audits
                if r["world"] == world.name and r["strategy"] == strategy
            ]
            assert len(selected) == len(set(selected)) == 4


@pytest.mark.parametrize("budgets", [(), (0,), (257,), (1.5,)])
def test_invalid_budgets(budgets):
    with pytest.raises(ValueError):
        run_temporal(budgets=budgets)
