import ast
import json

import pytest

from codeguard.acquisition import Candidate, information, run
from codeguard.corpus import CLASSES, TRANSFORMS, base_source, build, load, transform
from codeguard.experiment import parse_output


def test_corpus_groups_and_invariants(tmp_path):
    path = tmp_path / "data.jsonl"
    rows = build(path)
    assert len(load(path)) == 144
    assert len({r["family"] for r in rows if r["split"] == "test"}) == 9
    assert len({r["sample_id"] for r in rows}) == 144
    for r in rows:
        ast.parse(r["source"])
    for category in CLASSES:
        for i in range(6):
            for v in (True, False):
                for kind in TRANSFORMS:
                    assert transform(base_source(category, i, v), kind)


def test_corrupt_source_rejected(tmp_path):
    p = tmp_path / "data"
    rows = build(p)
    rows[0]["source"] = "pass\n"
    p.write_text("\n".join(json.dumps(r) for r in rows))
    with pytest.raises(ValueError, match="hash"):
        load(p)


def test_parser_never_converts_bad_output_to_clean():
    good = json.dumps({c: False for c in CLASSES})
    assert parse_output(good) == {c: False for c in CLASSES}
    for bad in ("", "{}", good + " explanation", good.replace("false", '"false"'), "I refuse"):
        with pytest.raises((ValueError, json.JSONDecodeError)):
            parse_output(bad)


@pytest.mark.parametrize(
    "strategy",
    [
        "random",
        "fixed",
        "full",
        "outcome_only",
        "policy_only",
        "no_policy",
        "no_boundary",
        "no_novelty",
    ],
)
def test_query_budget_no_repeats_and_replay(strategy):
    candidates = [Candidate(str(i), str(i % 3), str(i // 2)) for i in range(12)]
    seen = []

    def query(s):
        seen.append(s)
        return int(s) % 2 == 0

    snapshots, trace = run(candidates, query, strategy, [3, 6], 17)
    assert len(seen) == 6 and len(set(seen)) == 6
    assert set(snapshots) == {3, 6}
    again, _ = run(candidates, lambda s: int(s) % 2 == 0, strategy, [3, 6], 17)
    assert snapshots == again
    assert all(0 < p < 1 for p in snapshots[6].values())
    assert set(Candidate.__dataclass_fields__) == {"sample_id", "cell", "family"}


def test_information_decreases_with_repeated_balanced_evidence():
    assert information(1, 1)[0] > information(10, 10)[0] > 0
    assert information(1, 1)[1] >= 0


def test_invalid_feedback_rejected():
    with pytest.raises(ValueError):
        run([Candidate("x", "c", "f")], lambda _: None, "full", [1], 0)


def test_confusion_matrix_hand_calculation():
    from codeguard.analysis import confusion

    got = confusion(
        [True] * 4 + [False] * 6, [True, True, True, False, True, False, False, False, False, False]
    )
    assert (got["tp"], got["fn"], got["fp"], got["tn"]) == (3, 1, 1, 5)
    assert got["recall"] == 0.75 and got["precision"] == 0.75
    assert got["fpr"] == pytest.approx(1 / 6)
    assert confusion([], [])["recall"] is None
    with pytest.raises(ValueError):
        confusion([True], [])


def test_family_leakage_rejected(tmp_path):
    p = tmp_path / "data"
    rows = build(p)
    rows[0]["split"] = "test"
    p.write_text("\n".join(json.dumps(r) for r in rows))
    with pytest.raises(ValueError, match="family"):
        load(p)


def test_invalid_status_excluded_and_coverage_visible():
    from codeguard.analysis import summary

    rows = [
        {"sample_id": "a", "vulnerable": True, "category": "sql_injection"},
        {"sample_id": "b", "vulnerable": False, "category": "sql_injection"},
    ]
    out = {
        "a": {"status": "invalid_output", "predictions": None},
        "b": {"status": "ok", "predictions": {c: False for c in CLASSES}},
    }
    got = summary(rows, out)
    assert got["coverage"] == 0.5
    assert got["target_class"]["recall"] is None
    assert got["target_class"]["fn"] == 0  # not silently scored as a clean prediction


def test_synthetic_trigger_demo_is_explicit_and_controlled():
    from codeguard.trigger_demo import demonstrate

    d = demonstrate()
    assert "NOT a poisoned" in d["disclosure"]
    for r in d["results"]:
        assert r["clean"]["sql_injection"] is True
        assert r["synthetic_compromised"]["sql_injection"] == (r["condition"] != "trigger")


def test_summary_wrong_class_counts_fp_and_missed_true_class():
    from codeguard.analysis import summary

    rows = [{"sample_id": "a", "vulnerable": True, "category": "sql_injection"}]
    out = {
        "a": {
            "status": "ok",
            "predictions": {
                "sql_injection": False,
                "command_injection": True,
                "path_traversal": False,
            },
        }
    }
    got = summary(rows, out)
    assert got["micro_all_classes"]["fp"] == 1
    assert got["micro_all_classes"]["fn"] == 1
