import json
import shutil
import subprocess
from pathlib import Path

import pytest

from code_agent_eval.corpus import load_corpus
from code_agent_eval.semgrep_runner import run_semgrep

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("mode", ["missing", "timeout", "exit", "errors", "partial"])
def test_semgrep_failure_never_becomes_clean_scan(monkeypatch, mode):
    def fake_run(*args, **kwargs):
        if mode == "missing":
            raise FileNotFoundError()
        if mode == "timeout":
            raise subprocess.TimeoutExpired("semgrep", 120)
        payload = {"errors": ["bad"] if mode == "errors" else [], "paths": {"scanned": []}}
        return subprocess.CompletedProcess(
            [], 2 if mode == "exit" else 0, json.dumps(payload), "failed"
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(RuntimeError):
        run_semgrep(load_corpus(ROOT / "samples"), ROOT / "rules/semgrep.yml")


@pytest.mark.skipif(shutil.which("semgrep") is None, reason="Semgrep optional extra absent")
def test_real_semgrep_baseline():
    report = run_semgrep(load_corpus(ROOT / "samples"), ROOT / "rules/semgrep.yml")
    assert (report.metrics.tp, report.metrics.fp, report.metrics.fn) == (3, 0, 0)
    assert report.rules_sha256
