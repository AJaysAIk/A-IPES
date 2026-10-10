"""Separate detector execution from class-aware evaluation."""

from .corpus import corpus_digest
from .llm_review import CodeReviewer
from .metrics import compute_metrics
from .schemas import CLASSES, EvaluationReport, ReviewInput, ReviewResult, Sample


def score_results(
    samples: tuple[Sample, ...],
    results: tuple[ReviewResult, ...],
    *,
    detector: str,
    version: str,
    rules_sha256: str | None = None,
) -> EvaluationReport:
    ids = [s.sample_id for s in samples]
    result_ids = [r.sample_id for r in results]
    if not ids or len(set(ids)) != len(ids):
        raise ValueError("Corpus must be nonempty with unique IDs")
    if len(set(result_ids)) != len(result_ids) or set(ids) != set(result_ids):
        raise ValueError("Exactly one result required per sample; failed scans are not negatives")
    by_id = {r.sample_id: r for r in results}
    truth, predictions = [], []
    per_class = {}
    for sample in samples:
        for finding in by_id[sample.sample_id].findings:
            if finding.sample_id != sample.sample_id or finding.line > len(
                sample.source.splitlines()
            ):
                raise ValueError("Finding has an invalid sample ID or source line")
    for category in CLASSES:
        expected = [category in s.expected for s in samples]
        predicted = [
            any(f.vulnerability == category for f in by_id[s.sample_id].findings) for s in samples
        ]
        per_class[category] = compute_metrics(expected, predicted)
        truth.extend(expected)
        predictions.extend(predicted)
    return EvaluationReport(
        detector=detector,
        detector_version=version,
        corpus_sha256=corpus_digest(samples),
        rules_sha256=rules_sha256,
        sample_count=len(samples),
        decision_count=len(truth),
        metrics=compute_metrics(truth, predictions),
        per_class=per_class,
        results=tuple(by_id[s.sample_id] for s in samples),
    )


def evaluate(samples: tuple[Sample, ...], reviewer: CodeReviewer) -> EvaluationReport:
    results = tuple(
        reviewer.review(ReviewInput(sample_id=s.sample_id, source=s.source)) for s in samples
    )
    return score_results(samples, results, detector=reviewer.name, version=reviewer.version)
