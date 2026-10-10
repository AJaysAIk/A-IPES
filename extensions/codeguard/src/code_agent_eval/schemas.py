"""Common validated contracts for corpus, reviewers, and reports."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Vulnerability = Literal["sql_injection", "command_injection", "path_traversal"]
CLASSES: tuple[Vulnerability, ...] = ("sql_injection", "command_injection", "path_traversal")


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ReviewInput(StrictModel):
    # An opaque ID and source only: reviewers do not receive ground truth or file names.
    sample_id: str
    source: str


class Sample(StrictModel):
    sample_id: str
    relative_path: str
    source: str
    expected: tuple[Vulnerability, ...]


class Finding(StrictModel):
    sample_id: str
    vulnerability: Vulnerability
    line: int = Field(ge=1)
    message: str = Field(min_length=1)


class ReviewResult(StrictModel):
    sample_id: str
    findings: tuple[Finding, ...] = ()


class Metrics(StrictModel):
    tp: int
    fp: int
    tn: int
    fn: int
    precision: float
    recall: float
    f1: float
    accuracy: float


class EvaluationReport(StrictModel):
    schema_version: str = "1.0"
    detector: str
    detector_version: str
    corpus_sha256: str
    rules_sha256: str | None = None
    sample_count: int
    decision_count: int
    metrics: Metrics
    per_class: dict[str, Metrics]
    results: tuple[ReviewResult, ...]
