from __future__ import annotations

import argparse
import json
from pathlib import Path

from ipes_guard.experiments import evaluate_guards


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="results/results.json")
    parser.add_argument("--raw-output", default="results/raw_predictions.csv")
    args = parser.parse_args()

    summary, raw = evaluate_guards()
    print(summary.to_string(index=False))

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary.to_dict(orient="records"), indent=2))

    raw_output = Path(args.raw_output)
    raw_output.parent.mkdir(parents=True, exist_ok=True)
    raw.to_csv(raw_output, index=False)


if __name__ == "__main__":
    main()
