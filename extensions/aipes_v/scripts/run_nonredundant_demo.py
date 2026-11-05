from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aipes_v.nonredundant import run_nonredundant_pilot


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the A-IPES-V v0.2 non-redundant specification pilot."
    )
    parser.add_argument("--budgets", default="1,2,3,5")
    parser.add_argument("--seeds", default="0,1,2,3,4,5,6,7,8,9")
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    budgets = tuple(int(x) for x in args.budgets.split(",") if x)
    seeds = tuple(int(x) for x in args.seeds.split(",") if x)
    rows = run_nonredundant_pilot(budgets=budgets, seeds=seeds)

    unsafe = [row for row in rows if row["unsafe_world"]]
    grouped = defaultdict(list)
    for row in unsafe:
        grouped[(row["strategy"], row["budget"])].append(row)

    print("strategy,budget,unsafe_detection_rate,mean_first_probe_when_detected")
    for (strategy, budget), group in sorted(
        grouped.items(), key=lambda item: (item[0][1], item[0][0])
    ):
        detection = sum(bool(row["violation_detected"]) for row in group) / len(group)
        detected = [
            row["first_violation_probe"]
            for row in group
            if row["first_violation_probe"] is not None
        ]
        first = sum(detected) / len(detected) if detected else float("nan")
        print(f"{strategy},{budget},{detection:.3f},{first:.3f}")

    safe = [row for row in rows if not row["unsafe_world"]]
    false_alarms = sum(bool(row["violation_detected"]) for row in safe)
    print(f"safe_world_false_alarms={false_alarms}/{len(safe)}")

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
