import pytest

from code_agent_eval.metrics import compute_metrics


def test_confusion_matrix():
    m = compute_metrics([True, True, False, False], [True, False, True, False])
    assert (m.tp, m.fp, m.tn, m.fn) == (1, 1, 1, 1)
    assert (m.precision, m.recall, m.f1, m.accuracy) == (0.5, 0.5, 0.5, 0.5)


@pytest.mark.parametrize("truth,pred", [([], []), ([True], [])])
def test_invalid_lengths(truth, pred):
    with pytest.raises(ValueError):
        compute_metrics(truth, pred)


def test_zero_denominators():
    m = compute_metrics([False], [False])
    assert (m.precision, m.recall, m.f1, m.accuracy) == (0, 0, 0, 1)


def test_nontrivial_ratios():
    m = compute_metrics([True, True, True, False], [True, True, False, True])
    assert m.precision == pytest.approx(2 / 3)
    assert m.recall == pytest.approx(2 / 3)
    assert m.f1 == pytest.approx(2 / 3)
    assert m.accuracy == 0.5
