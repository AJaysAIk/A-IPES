from __future__ import annotations

import argparse
from pathlib import Path

from ipes_guard.phase2_benchmark import run_phase2_policy_probe_experiment


def parse_int_list(value: str) -> tuple[int, ...]:
    return tuple(int(item.strip()) for item in value.split(",") if item.strip())


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Phase 2 policy-aligned probe benchmark.")
    parser.add_argument("--budgets", default="1,2,3,5,8,10")
    parser.add_argument("--seeds", default="0,1,2,3,4")
    parser.add_argument("--output-dir", default="results/phase2_policy_probe")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary, raw, selected = run_phase2_policy_probe_experiment(
        budgets=parse_int_list(args.budgets),
        seeds=parse_int_list(args.seeds),
    )
    summary.to_csv(output_dir / "summary.csv", index=False)
    raw.to_csv(output_dir / "raw.csv", index=False)
    selected.to_csv(output_dir / "selected_probes.csv", index=False)
    print(summary.to_string(index=False))
    print(f"\nSaved: {output_dir / 'summary.csv'}")
    print(f"Saved: {output_dir / 'raw.csv'}")
    print(f"Saved: {output_dir / 'selected_probes.csv'}")


if __name__ == "__main__":
    main()
