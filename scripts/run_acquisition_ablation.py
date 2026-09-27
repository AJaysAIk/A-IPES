from __future__ import annotations

import argparse
from pathlib import Path

from ipes_guard.acquisition_ablation import run_acquisition_ablation


def parse_int_list(value: str) -> tuple[int, ...]:
    return tuple(
        int(item.strip())
        for item in value.split(",")
        if item.strip()
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the A-IPES acquisition-function ablation."
    )
    parser.add_argument(
        "--benchmark-seeds",
        default=",".join(str(index) for index in range(30)),
    )
    parser.add_argument("--budgets", default="2,5")
    parser.add_argument("--probe-seed", type=int, default=0)
    parser.add_argument(
        "--output-dir",
        default="results/acquisition_ablation_30",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    summary, per_benchmark, raw, selected, manifests = (
        run_acquisition_ablation(
            benchmark_seeds=parse_int_list(args.benchmark_seeds),
            budgets=parse_int_list(args.budgets),
            probe_seed=args.probe_seed,
        )
    )

    outputs = {
        "summary.csv": summary,
        "per_benchmark.csv": per_benchmark,
        "raw.csv": raw,
        "selected_probes.csv": selected,
        "benchmark_manifests.csv": manifests,
    }

    for filename, frame in outputs.items():
        frame.to_csv(output_dir / filename, index=False)

    print(summary.to_string(index=False))

    for filename in outputs:
        print(f"Saved: {output_dir / filename}")


if __name__ == "__main__":
    main()
