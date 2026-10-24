from __future__ import annotations

import argparse
import json
import hashlib
import sys
import time
from importlib.metadata import version
from pathlib import Path

from ipes_guard.benchmark_v2 import run_benchmark_v2


def parse_int_list(value: str) -> tuple[int, ...]:
    return tuple(int(item.strip()) for item in value.split(",") if item.strip())


def main() -> None:
    parser = argparse.ArgumentParser(description="Run independent Benchmark V2 replicates.")
    parser.add_argument("--benchmark-seeds", default=",".join(str(i) for i in range(30)))
    parser.add_argument("--budgets", default="1,2,3,5")
    parser.add_argument("--probe-seed", type=int, default=0)
    parser.add_argument("--prior-mode", choices=("legacy", "matched_full"), default="legacy")
    parser.add_argument("--output-dir", default="results/benchmark_v2")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    seeds = parse_int_list(args.benchmark_seeds)
    budgets = parse_int_list(args.budgets)
    if not seeds or len(set(seeds)) != len(seeds) or not budgets or min(budgets) < 1:
        raise ValueError("Provide unique world seeds and positive budgets")
    output_dir.mkdir(parents=True, exist_ok=False)
    root = Path(__file__).resolve().parents[1]
    manifest = {"status": "started", "prior_mode": args.prior_mode, "benchmark_seeds": seeds,
        "budgets": budgets, "probe_seed": args.probe_seed, "python": sys.version,
        "executable": sys.executable, "packages": {p: version(p) for p in ["numpy", "pandas", "scipy", "scikit-learn"]},
        "source_sha256": {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in ["src", "scripts"] for p in sorted((root/folder).rglob("*.py"))}}
    (output_dir/"run_manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    started = time.monotonic()
    summary, per_benchmark, raw, selected, manifests = run_benchmark_v2(
        benchmark_seeds=parse_int_list(args.benchmark_seeds),
        budgets=parse_int_list(args.budgets),
        probe_seed=args.probe_seed,
        prior_mode=args.prior_mode,
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
    manifest.update(status="complete", elapsed_seconds=time.monotonic()-started)
    (output_dir/"run_manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    print(summary.to_string(index=False))
    for name in outputs:
        print(f"Saved: {output_dir / name}")


if __name__ == "__main__":
    main()
