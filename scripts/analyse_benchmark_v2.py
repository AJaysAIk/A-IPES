from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


METRICS = (
    "attack_recall",
    "false_positive_rate",
    "balanced_accuracy",
    "policy_exact_match",
    "effect_mae",
    "shifted_attack_recall",
)


def paired_bootstrap(values: np.ndarray, samples: int, seed: int) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    n = len(values)
    means = np.empty(samples, dtype=float)
    for i in range(samples):
        means[i] = values[rng.integers(0, n, size=n)].mean()
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def sign_flip_pvalue(values: np.ndarray, samples: int, seed: int) -> float:
    rng = np.random.default_rng(seed)
    observed = abs(float(values.mean()))
    null = np.empty(samples, dtype=float)
    for i in range(samples):
        signs = rng.choice((-1.0, 1.0), size=len(values))
        null[i] = abs(float((values * signs).mean()))
    return float((1 + np.sum(null >= observed)) / (samples + 1))


def main() -> None:
    parser = argparse.ArgumentParser(description="Paired A-IPES versus passive analysis.")
    parser.add_argument("--input", default="results/benchmark_v2/per_benchmark.csv")
    parser.add_argument("--output", default="results/benchmark_v2/paired_active_vs_passive.csv")
    parser.add_argument("--bootstrap-samples", type=int, default=10_000)
    parser.add_argument("--permutation-samples", type=int, default=20_000)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()

    frame = pd.read_csv(args.input)
    rows: list[dict] = []
    for budget in sorted(frame["budget"].unique()):
        subset = frame[frame["budget"] == budget]
        active = subset[subset["strategy"] == "policy_active"].set_index("benchmark_seed")
        passive = subset[subset["strategy"] == "passive_characterisation"].set_index("benchmark_seed")
        shared = active.index.intersection(passive.index)
        for metric in METRICS:
            differences = (active.loc[shared, metric] - passive.loc[shared, metric]).to_numpy(float)
            low, high = paired_bootstrap(differences, args.bootstrap_samples, args.seed + int(budget))
            rows.append({
                "budget": budget,
                "metric": metric,
                "n_benchmarks": len(differences),
                "active_mean": float(active.loc[shared, metric].mean()),
                "passive_mean": float(passive.loc[shared, metric].mean()),
                "mean_difference_active_minus_passive": float(differences.mean()),
                "ci95_low": low,
                "ci95_high": high,
                "sign_flip_pvalue": sign_flip_pvalue(differences, args.permutation_samples, args.seed + 100 + int(budget)),
            })
    result = pd.DataFrame(rows)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False)
    print(result.to_string(index=False))
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()
