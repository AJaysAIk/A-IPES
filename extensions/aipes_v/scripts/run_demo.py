from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aipes_v.benchmark import run_pilot


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the A-IPES-V synthetic specification-monitoring pilot.")
    parser.add_argument("--budgets", default="1,2,3,5")
    parser.add_argument("--seeds", default="0,1,2,3,4")
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    budgets = tuple(int(x) for x in args.budgets.split(",") if x)
    seeds = tuple(int(x) for x in args.seeds.split(",") if x)
    rows = run_pilot(budgets=budgets, seeds=seeds)

    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["strategy"], row["budget"])].append(row)

    print("strategy,budget,violation_detection_rate,mean_specification_coverage")
    for (strategy, budget), group in sorted(grouped.items(), key=lambda x: (x[0][1], x[0][0])):
        detection = sum(bool(r["violation_detected"]) for r in group) / len(group)
        coverage = sum(float(r["specification_coverage"]) for r in group) / len(group)
        print(f"{strategy},{budget},{detection:.3f},{coverage:.3f}")

    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        print(f"Saved raw rows: {path}")


if __name__ == "__main__":
    main()
