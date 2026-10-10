"""JSON-only stdout for reproducible command-line runs."""

import argparse
import sys
from pathlib import Path

from rich.console import Console

from .corpus import load_corpus
from .evaluator import evaluate
from .llm_review import MockReviewer
from .semgrep_runner import run_semgrep


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--detector", choices=("mock", "semgrep"), default="mock")
    parser.add_argument("--corpus", type=Path, default=Path("samples"))
    parser.add_argument("--rules", type=Path, default=Path("rules/semgrep.yml"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        samples = load_corpus(args.corpus)
        report = (
            evaluate(samples, MockReviewer())
            if args.detector == "mock"
            else run_semgrep(samples, args.rules)
        )
        output = report.model_dump_json(indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output + "\n", encoding="utf-8")
        print(output)
    except (OSError, ValueError, RuntimeError) as exc:
        Console(stderr=True).print(f"Evaluation failed: {exc}", markup=False)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
