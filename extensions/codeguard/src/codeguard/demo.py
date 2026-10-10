"""Recorded real-model demonstration; no model call and no fixture execution."""

import json
from pathlib import Path

from .corpus import load


def main():
    root = Path("codeguard")
    rows = load(root / "corpus/manifest.jsonl")
    model = {
        r["sample_id"]: r
        for r in map(json.loads, (root / "results/model.jsonl").read_text().splitlines())
    }
    static = {
        r["sample_id"]: r for r in json.loads((root / "results/static.json").read_text())["results"]
    }
    originals = [
        r
        for r in rows
        if r["split"] == "test"
        and r["vulnerable"]
        and r["category"] == "sql_injection"
        and r["transformation"] == "original"
    ]
    pairs = []
    for a in originals:
        b = next(
            r
            for r in rows
            if r["family"] == a["family"] and r["vulnerable"] and r["transformation"] == "renamed"
        )
        if (
            model[a["sample_id"]]["predictions"]["sql_injection"]
            and not model[b["sample_id"]]["predictions"]["sql_injection"]
        ):
            pairs.append((a, b))
    if not pairs:
        raise ValueError("No matching recorded example")
    print("RECORDED REAL-MODEL REPLAY - no live inference; source is never executed.")
    print(
        "Illustrative example selected after evaluation; aggregate results are reported separately."
    )
    for row in pairs[0]:
        sid = row["sample_id"]
        print("\nRepresentation:", row["transformation"], "| ID:", sid)
        print(row["source"])
        print("Frozen local model:", model[sid]["raw"])
        print("Semgrep SQL finding:", static[sid]["predictions"]["sql_injection"])
        print(
            "Hybrid SQL finding:",
            static[sid]["predictions"]["sql_injection"]
            or model[sid]["predictions"]["sql_injection"],
        )
    s = json.loads((root / "results/summary.json").read_text())
    print("\nHeld-out aggregate; correlated variants, 9 base families:")
    for name in ("model", "semgrep", "hybrid"):
        m = s["metrics"]["test"][name]["target_class"]
        print(f"{name}: {m['tp']}/36 detected; {m['fp']}/36 safe cases flagged")
    print("Hybrid equals Semgrep here. This does not prove production security.")


if __name__ == "__main__":
    main()
