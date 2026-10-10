from pathlib import Path

import pytest

from code_agent_eval.corpus import load_corpus
from code_agent_eval.evaluator import evaluate, score_results
from code_agent_eval.llm_review import MockReviewer
from code_agent_eval.schemas import Finding, ReviewResult


@pytest.fixture
def samples():
    return load_corpus(Path(__file__).resolve().parents[1] / "samples")


def score(samples, results):
    return score_results(samples, results, detector="test", version="1")


def test_mock_deterministic(samples):
    a = evaluate(samples, MockReviewer())
    assert a == evaluate(samples, MockReviewer())
    assert (a.metrics.tp, a.metrics.tn, a.metrics.fp, a.metrics.fn) == (3, 15, 0, 0)
    assert a.decision_count == 18


def test_wrong_class_is_fp_and_fn_and_duplicates_count_once(samples):
    finding = Finding(
        sample_id=samples[0].sample_id,
        vulnerability="command_injection",
        line=1,
        message="Wrong class",
    )
    results = tuple(
        ReviewResult(sample_id=s.sample_id, findings=(finding, finding) if i == 0 else ())
        for i, s in enumerate(samples)
    )
    report = score(samples, results)
    assert (report.metrics.tp, report.metrics.fp, report.metrics.fn) == (0, 1, 3)


@pytest.mark.parametrize("mode", ["missing", "duplicate", "unknown", "bad_line", "bad_id"])
def test_invalid_results_rejected(samples, mode):
    results = list(evaluate(samples, MockReviewer()).results)
    if mode == "missing":
        results.pop()
    elif mode == "duplicate":
        results.append(results[0])
    elif mode == "unknown":
        results[0] = ReviewResult(sample_id="unknown")
    else:
        finding = Finding(
            sample_id="wrong" if mode == "bad_id" else samples[0].sample_id,
            vulnerability="sql_injection",
            line=999 if mode == "bad_line" else 1,
            message="invalid",
        )
        results[0] = ReviewResult(sample_id=samples[0].sample_id, findings=(finding,))
    with pytest.raises(ValueError):
        score(samples, tuple(results))


def test_provider_failure_propagates(samples):
    class BrokenReviewer:
        name, version = "broken", "1"

        def review(self, sample):
            assert set(sample.model_dump()) == {"sample_id", "source"}
            raise RuntimeError("provider unavailable")

    with pytest.raises(RuntimeError, match="provider unavailable"):
        evaluate(samples, BrokenReviewer())
