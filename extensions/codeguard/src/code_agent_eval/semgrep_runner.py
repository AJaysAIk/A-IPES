"""Run local Semgrep rules against isolated text fixtures with fail-closed scoring."""

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from .evaluator import score_results
from .schemas import CLASSES, EvaluationReport, Finding, ReviewResult, Sample


def run_semgrep(samples: tuple[Sample, ...], rules: Path) -> EvaluationReport:
    rules = rules.resolve()
    rules_bytes = rules.read_bytes()
    with tempfile.TemporaryDirectory(prefix="code-agent-eval-") as directory:
        root = Path(directory)
        for sample in samples:
            (root / f"{sample.sample_id}.py").write_text(sample.source, encoding="utf-8")
        command = [
            "semgrep",
            "scan",
            "--config",
            str(rules),
            "--json",
            "--metrics=off",
            "--disable-version-check",
            "--no-git-ignore",
            "--strict",
            str(root),
        ]
        try:
            process = subprocess.run(command, capture_output=True, text=True, timeout=120)
        except FileNotFoundError as exc:
            raise RuntimeError("Semgrep unavailable; install the semgrep extra") from exc
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError("Semgrep exceeded the 120-second timeout") from exc
        if process.returncode != 0:
            raise RuntimeError(f"Semgrep failed ({process.returncode}): {process.stderr[-2000:]}")
        payload = json.loads(process.stdout)
        if payload.get("errors"):
            raise RuntimeError(f"Semgrep reported scan errors: {payload['errors']}")
        scanned = {Path(p).name for p in payload.get("paths", {}).get("scanned", [])}
        required = {f"{s.sample_id}.py" for s in samples}
        if scanned != required:
            raise RuntimeError("Semgrep did not scan exactly the requested corpus")
        findings: dict[str, list[Finding]] = {s.sample_id: [] for s in samples}
        for match in payload["results"]:
            sample_id = Path(match["path"]).stem
            category = match["check_id"].split(".")[-1]
            if sample_id not in findings or category not in CLASSES:
                raise RuntimeError("Unrecognised Semgrep sample or rule")
            findings[sample_id].append(
                Finding(
                    sample_id=sample_id,
                    vulnerability=category,
                    line=match["start"]["line"],
                    message=match["extra"]["message"],
                )
            )
        results = tuple(
            ReviewResult(
                sample_id=s.sample_id,
                findings=tuple(
                    sorted(findings[s.sample_id], key=lambda f: (f.line, f.vulnerability))
                ),
            )
            for s in samples
        )
    return score_results(
        samples,
        results,
        detector="semgrep",
        version=payload["version"],
        rules_sha256=hashlib.sha256(rules_bytes).hexdigest(),
    )
