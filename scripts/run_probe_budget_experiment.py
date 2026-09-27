from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from ipes_guard.budget_experiments import run_probe_budget_experiment


def _parse_ints(value: str) -> tuple[int, ...]:
    return tuple(int(item.strip()) for item in value.split(",") if item.strip())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--budgets", default="1,2,3,5,8,10")
    parser.add_argument("--seeds", default="0,1,2,3,4")
    parser.add_argument("--output-dir", default="results/probe_budget")
    args = parser.parse_args()

    summary, raw = run_probe_budget_experiment(
        budgets=_parse_ints(args.budgets),
        seeds=_parse_ints(args.seeds),
    )

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    summary.to_csv(out / "summary.csv", index=False)
    raw.to_csv(out / "raw.csv", index=False)

    print(summary.to_string(index=False))
    print(f"\nSaved: {out / 'summary.csv'}")
    print(f"Saved: {out / 'raw.csv'}")


if __name__ == "__main__":
    main()
