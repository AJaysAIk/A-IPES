import random

import pytest
from aipes_v.misspecification import (
    LeaseExperiment,
    LeaseWorld,
    lease_monitor,
    model_order,
    outcome_status,
)


@pytest.fixture(scope="module")
def experiment():
    return LeaseExperiment()


def test_lease_boundary_refusal_and_regrant():
    world = LeaseWorld("compliant", False)
    valid = ("grant", "idle", "use")
    expired = ("grant", "idle", "idle", "use")
    assert world.execute(valid)[-1][0]
    assert not world.execute(expired)[-1][0]
    assert not lease_monitor(expired, world.execute(expired))
    assert lease_monitor(expired, ((False, False),) * 3 + ((True, False),))
    regrant = ("grant", "idle", "idle", "grant", "use")
    assert world.execute(regrant)[-1][0]
    assert not lease_monitor(regrant, world.execute(regrant))
    revoked = ("grant", "revoke", "use")
    assert not world.execute(revoked)[-1][0]
    assert lease_monitor(revoked, ((False, False), (False, False), (True, False)))


def test_distinct_failure_mechanisms():
    early = ("use",)
    stale = ("grant", "revoke", "use")
    late = ("grant", "idle", "idle", "use")
    assert lease_monitor(early, LeaseWorld("early", False).execute(early))
    assert lease_monitor(stale, LeaseWorld("stale", False).execute(stale))
    assert lease_monitor(late, LeaseWorld("late", False).execute(late))
    assert not lease_monitor(stale, LeaseWorld("late", False).execute(stale))
    assert not lease_monitor(early, LeaseWorld("stale", False).execute(early))
    with pytest.raises(ValueError):
        lease_monitor(stale, ())
    with pytest.raises(ValueError):
        LeaseWorld("compliant", False).execute(("unknown",))


def test_exhaustive_labels(experiment):
    assert len(experiment.pool) == 4096
    assert len(experiment.oracle) == 12
    assert sum(r["unsafe_world"] for r in experiment.oracle) == 8
    assert sum(r["out_of_class"] for r in experiment.oracle) == 10
    assert all(r["traces_checked"] == 4096 for r in experiment.oracle)
    assert all(
        bool(r["equivalent_models"]) != r["out_of_class"] for r in experiment.oracle
    )


def test_safe_world_can_refute_every_model(experiment):
    trace = ("grant", "idle", "idle", "use", "idle", "idle")
    index = experiment.pool.index(trace)
    response = LeaseWorld("compliant", False).execute(trace)
    assert not lease_monitor(trace, response)
    assert not any(rs[index] == response for rs in experiment.predictions)
    assert outcome_status(False, True) == "model_inadequate_without_violation"
    assert outcome_status(False, False) == "no_counterexample_observed"
    assert outcome_status(True, True) == "violation_observed"
    chosen, work = experiment.choose("specification_active", [index, 0], ())
    assert chosen == index
    assert work["logical_response_lookups"] == 0


def test_ceg_model_order_is_seeded_and_counterexamples_are_validated(experiment):
    assert model_order(0) == model_order(0)
    assert model_order(0) != model_order(1)
    assert sorted(model_order(0)) == list(range(8))
    order = list(range(len(experiment.pool)))
    random.Random(0).shuffle(order)
    chosen, work = experiment.choose("counterexample_guided", order, model_order(0))
    first_model = model_order(0)[0]
    assert experiment.violations[first_model][chosen]
    assert work["logical_violation_lookups"] > 0
    trace = experiment.pool[chosen]
    response = LeaseWorld("compliant", False).execute(trace)
    assert not lease_monitor(trace, response)
    assert experiment.predictions[first_model][chosen] != response


def test_reproducibility_prefixes_and_sticky_mismatch(experiment):
    rows, audits = experiment.run(budgets=(1, 2, 4), seeds=(0,))
    assert (rows, audits) == experiment.run(budgets=(1, 2, 4), seeds=(0,))
    short_rows, short_audits = experiment.run(budgets=(1, 2), seeds=(0,))
    assert short_rows == [r for r in rows if r["budget"] <= 2]
    assert short_audits == [r for r in audits if r["query"] <= 2]
    assert all(
        r["action_calls"] == 6 * r["query"] and r["resets"] == r["query"]
        for r in audits
    )
    assert all(not r["violation_detected"] for r in rows if not r["unsafe_world"])
    assert all(not r["model_inadequate"] for r in rows if not r["out_of_class"])
    collapsed = set()
    selected = {}
    for audit in audits:
        key = audit["world"], audit["strategy"], audit["seed"]
        if key in collapsed:
            assert audit["posterior_before"] == audit["posterior_after"] == 0
            assert audit["model_inadequate"]
            assert audit["candidate_checks"] == 1
        if not audit["posterior_after"]:
            collapsed.add(key)
        traces = selected.setdefault(key, set())
        assert audit["trace"] not in traces
        traces.add(audit["trace"])
    assert collapsed
    assert all(r["status"] != "safe" for r in rows)


@pytest.mark.parametrize("budgets", [(), (0,), (4097,), (1.5,), (True,)])
def test_invalid_budgets(experiment, budgets):
    with pytest.raises(ValueError):
        experiment.run(budgets=budgets)
