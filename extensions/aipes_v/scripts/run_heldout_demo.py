from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aipes_v.heldout import run_heldout_pilot


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run A-IPES-V v0.4 held-out contextual-world evaluation."
    )
    parser.add_argument("--budgets", default="1,2,3")
    parser.add_argument("--seeds", default=",".join(str(i) for i in range(20)))
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    budgets = tuple(int(x) for x in args.budgets.split(",") if x)
    seeds = tuple(int(x) for x in args.seeds.split(",") if x)
    rows = run_heldout_pilot(budgets=budgets, seeds=seeds)

    unsafe = [r for r in rows if r["unsafe_world"]]
    groups = defaultdict(list)
    for row in unsafe:
        groups[(row["strategy"], row["budget"])].append(row)

    print("strategy,budget,unsafe_detection_rate,mean_first_probe_when_detected")
    for (strategy, budget), group in sorted(
        groups.items(), key=lambda item: (item[0][1], item[0][0])
    ):
        detected = [r for r in group if r["violation_detected"]]
        rate = len(detected) / len(group)
        first = (
            sum(r["first_violation_probe"] for r in detected) / len(detected)
            if detected
            else float("nan")
        )
        print(f"{strategy},{budget},{rate:.3f},{first:.3f}")

    safe = [r for r in rows if not r["unsafe_world"]]
    false_alarms = sum(bool(r["violation_detected"]) for r in safe)
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
