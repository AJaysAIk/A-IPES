from __future__ import annotations

import argparse
from pathlib import Path

from ipes_guard.benchmark_v2 import run_benchmark_v2


def parse_int_list(value: str) -> tuple[int, ...]:
    return tuple(int(item.strip()) for item in value.split(",") if item.strip())


def main() -> None:
    parser = argparse.ArgumentParser(description="Run independent Benchmark V2 replicates.")
    parser.add_argument("--benchmark-seeds", default=",".join(str(i) for i in range(30)))
    parser.add_argument("--budgets", default="1,2,3,5")
    parser.add_argument("--probe-seed", type=int, default=0)
    parser.add_argument("--output-dir", default="results/benchmark_v2")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary, per_benchmark, raw, selected, manifests = run_benchmark_v2(
        benchmark_seeds=parse_int_list(args.benchmark_seeds),
        budgets=parse_int_list(args.budgets),
        probe_seed=args.probe_seed,
    )
    outputs = {
        "summary.csv": summary,
        "per_benchmark.csv": per_benchmark,
        "raw.csv": raw,
        "selected_probes.csv": selected,
        "benchmark_manifests.csv": manifests,
    }
    for name, frame in outputs.items():
        frame.to_csv(output_dir / name, index=False)
    print(summary.to_string(index=False))
    for name in outputs:
        print(f"Saved: {output_dir / name}")


if __name__ == "__main__":
    main()
