import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_cli_json_and_saved_output(tmp_path):
    output = tmp_path / "report.json"
    result = subprocess.run(
        [sys.executable, "-m", "code_agent_eval.cli", "--output", str(output)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(result.stdout) == json.loads(output.read_text())
    assert json.loads(result.stdout)["sample_count"] == 6


def test_missing_corpus_has_nonzero_exit(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "code_agent_eval.cli", "--corpus", str(tmp_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert result.stdout == ""
