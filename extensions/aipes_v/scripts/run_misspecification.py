from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from aipes_v.misspecification import LeaseExperiment


def main():
    parser = argparse.ArgumentParser(
        description="Frozen v0.6 model inadequacy experiment"
    )
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    experiment = LeaseExperiment()
    rows, audits = experiment.run()
    path = Path(args.output_dir)
    path.mkdir(parents=True, exist_ok=True)
    with (path / "rows.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with (path / "traces.jsonl").open("w") as handle:
        for audit in audits:
            handle.write(json.dumps(audit, sort_keys=True) + "\n")
    (path / "oracle.json").write_text(
        json.dumps(experiment.oracle, indent=2, sort_keys=True) + "\n"
    )
    summary = []
    for strategy in sorted({r["strategy"] for r in rows}):
        for budget in sorted({r["budget"] for r in rows}):
            group = [
                r for r in rows if r["strategy"] == strategy and r["budget"] == budget
            ]
            unsafe = [r for r in group if r["unsafe_world"]]
            safe = [r for r in group if not r["unsafe_world"]]
            ooc = [r for r in group if r["out_of_class"]]
            inc = [r for r in group if not r["out_of_class"]]
            summary.append(
                {
                    "strategy": strategy,
                    "budget": budget,
                    "unsafe_detections": sum(r["violation_detected"] for r in unsafe),
                    "unsafe_cases": len(unsafe),
                    "out_of_class_flags": sum(r["model_inadequate"] for r in ooc),
                    "out_of_class_cases": len(ooc),
                    "safe_alarms": sum(r["violation_detected"] for r in safe),
                    "safe_mismatches": sum(r["model_inadequate"] for r in safe),
                    "safe_cases": len(safe),
                    "false_mismatches": sum(r["model_inadequate"] for r in inc),
                    "in_class_cases": len(inc),
                    "total_candidate_checks": sum(r["candidate_checks"] for r in group),
                    "total_logical_response_lookups": sum(
                        r["logical_response_lookups"] for r in group
                    ),
                    "total_logical_violation_lookups": sum(
                        r["logical_violation_lookups"] for r in group
                    ),
                    "total_refinement_lookups": sum(
                        r["refinement_response_lookups"] for r in group
                    ),
                }
            )
    with (path / "summary.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    groups = defaultdict(list)
    for row in rows:
        groups[row["strategy"], row["budget"], row["kind"]].append(row)
    print("strategy,budget,kind,violations,mismatches,total")
    for (strategy, budget, kind), group in sorted(groups.items()):
        print(
            f"{strategy},{budget},{kind},"
            f"{sum(r['violation_detected'] for r in group)},"
            f"{sum(r['model_inadequate'] for r in group)},{len(group)}"
        )
    print(f"rows={len(rows)} audited_queries={len(audits)}")


if __name__ == "__main__":
    main()
