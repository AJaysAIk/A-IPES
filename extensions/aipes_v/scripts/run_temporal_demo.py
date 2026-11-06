from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from aipes_v.temporal import run_temporal


def main():
    parser = argparse.ArgumentParser(
        description="Frozen v0.5 bounded temporal experiment"
    )
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    rows, audits = run_temporal()
    path = Path(args.output_dir)
    path.mkdir(parents=True, exist_ok=True)
    with (path / "rows.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with (path / "traces.jsonl").open("w") as handle:
        for audit in audits:
            handle.write(json.dumps(audit, sort_keys=True) + "\n")
    groups = defaultdict(list)
    for row in rows:
        kind = row["world"].split("_pulse")[0]
        groups[row["strategy"], row["budget"], kind].append(row)
    print("strategy,trace_budget,mutant,detected,total")
    for (strategy, budget, kind), group in sorted(groups.items()):
        print(
            f"{strategy},{budget},{kind},"
            f"{sum(r['violation_detected'] for r in group)},{len(group)}"
        )
    print(f"rows={len(rows)} audited_queries={len(audits)}")


if __name__ == "__main__":
    main()
