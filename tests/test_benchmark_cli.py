"""Exercise the installed benchmark-to-analysis path on a development world.

These are software integration checks, not evidence of generalisation.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]


def run_script(name, *args):
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / name), *map(str, args)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )


@pytest.mark.parametrize("mode", ["legacy", "matched_full"])
def test_benchmark_analysis_and_overwrite_protection(tmp_path, mode):
    output = tmp_path / mode
    args = (
        "--benchmark-seeds",
        "0",
        "--budgets",
        "1",
        "--prior-mode",
        mode,
        "--output-dir",
        output,
    )
    result = run_script("run_benchmark_v2.py", *args)
    assert result.returncode == 0, result.stderr
    manifest = json.loads((output / "run_manifest.json").read_text())
    assert manifest["status"] == "complete"
    assert manifest["prior_mode"] == mode
    assert manifest["benchmark_seeds"] == [0]
    assert manifest["budgets"] == [1]
    for relative, digest in manifest["source_sha256"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
    for name in (
        "summary",
        "per_benchmark",
        "raw",
        "selected_probes",
        "benchmark_manifests",
    ):
        frame = pd.read_csv(output / f"{name}.csv")
        assert not frame.empty
        assert set(frame["prior_mode"]) == {mode}
    if mode == "legacy":
        # Compare schedules unaffected by the maximum requested budget.
        # Random choice(size=max_budget) differs from the archived max-budget-5 run.
        archived = pd.read_csv(ROOT / "results/benchmark_v2_30/per_benchmark.csv")
        archived = archived[
            (archived["benchmark_seed"] == 0) & (archived["budget"] == 1)
        ]
        current = pd.read_csv(output / "per_benchmark.csv")
        current = current[current["strategy"] != "random"]
        archived = archived[archived["strategy"] != "random"]
        metrics = [
            "attack_recall",
            "false_positive_rate",
            "balanced_accuracy",
            "policy_exact_match",
            "effect_mae",
            "shifted_attack_recall",
        ]
        np.testing.assert_allclose(
            current.set_index("strategy").sort_index()[metrics],
            archived.set_index("strategy").sort_index()[metrics],
            rtol=0,
            atol=1e-12,
        )
    raw = pd.read_csv(output / "raw.csv")
    if mode == "matched_full":
        counts = raw.groupby("tool_name")["prior_fingerprint"].nunique()
        assert (counts == 1).all()
    traces = pd.read_csv(output / "selected_probes.csv")
    active = traces[traces["strategy"] == "policy_active"]
    assert all(
        json.loads(trace)["probe_index"] == 1 for trace in active["diagnostic_trace"]
    )
    analysis = output / "paired.csv"
    result = run_script(
        "analyse_benchmark_v2.py",
        "--input",
        output / "per_benchmark.csv",
        "--output",
        analysis,
        "--bootstrap-samples",
        "20",
        "--permutation-samples",
        "20",
    )
    assert result.returncode == 0, result.stderr
    paired = pd.read_csv(analysis)
    assert len(paired) == 6
    assert (paired["n_benchmarks"] == 1).all()
    assert set(paired["prior_mode"]) == {mode}
    assert np.isfinite(paired.select_dtypes(include="number").to_numpy()).all()
    # A second invocation must fail without changing any existing result.
    before = {p.name: p.read_bytes() for p in output.iterdir()}
    result = run_script("run_benchmark_v2.py", *args)
    assert result.returncode != 0
    assert before == {p.name: p.read_bytes() for p in output.iterdir()}
