"""Binary metrics with an explicit zero-division policy."""

from collections.abc import Sequence

from .schemas import Metrics


def compute_metrics(expected: Sequence[bool], predicted: Sequence[bool]) -> Metrics:
    if len(expected) != len(predicted) or not expected:
        raise ValueError("Expected equal, nonempty decision sequences")
    tp = sum(a and b for a, b in zip(expected, predicted, strict=True))
    fp = sum(not a and b for a, b in zip(expected, predicted, strict=True))
    tn = sum(not a and not b for a, b in zip(expected, predicted, strict=True))
    fn = sum(a and not b for a, b in zip(expected, predicted, strict=True))
    return Metrics(
        tp=tp,
        fp=fp,
        tn=tn,
        fn=fn,
        precision=tp / (tp + fp) if tp + fp else 0.0,
        recall=tp / (tp + fn) if tp + fn else 0.0,
        f1=2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0,
        accuracy=(tp + tn) / len(expected),
    )
