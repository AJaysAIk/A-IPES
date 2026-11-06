from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aipes_v.sensitivity import run_weight_sensitivity


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run A-IPES-V v0.3 acquisition-weight sensitivity."
    )
    parser.add_argument("--budgets", default="1,2")
    parser.add_argument("--seeds", default="0,1,2,3,4,5,6,7,8,9")
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    budgets = tuple(int(x) for x in args.budgets.split(",") if x)
    seeds = tuple(int(x) for x in args.seeds.split(",") if x)
    rows = run_weight_sensitivity(seeds=seeds, budgets=budgets)

    unsafe = [r for r in rows if r["unsafe_world"]]
    groups = defaultdict(list)
    for row in unsafe:
        key = (
            row["strategy"],
            row["specification_information"],
            row["expected_violation"],
            row["budget"],
        )
        groups[key].append(row)

    print(
        "strategy,specification_information,expected_violation,budget,"
        "unsafe_detection_rate,mean_first_probe_when_detected"
    )
    for key, group in sorted(groups.items(), key=lambda item: (item[0][3], item[0][0], item[0][1], item[0][2])):
        detected = [r for r in group if r["violation_detected"]]
        rate = len(detected) / len(group)
        first = (
            sum(r["first_violation_probe"] for r in detected) / len(detected)
            if detected
            else float("nan")
        )
        print(
            f"{key[0]},{key[1]:.3f},{key[2]:.3f},{key[3]},"
            f"{rate:.3f},{first:.3f}"
        )

    safe = [r for r in rows if not r["unsafe_world"]]
    safe_groups = defaultdict(list)
    for row in safe:
        key = (
            row["strategy"],
            row["specification_information"],
            row["expected_violation"],
            row["budget"],
        )
        safe_groups[key].append(row)

    print("safe_world_false_alarm_rates")
    for key, group in sorted(safe_groups.items(), key=lambda item: (item[0][3], item[0][0], item[0][1], item[0][2])):
        rate = sum(bool(r["violation_detected"]) for r in group) / len(group)
        print(f"{key[0]},{key[1]:.3f},{key[2]:.3f},{key[3]},{rate:.3f}")

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
