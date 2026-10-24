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


def validate_pairs(frame: pd.DataFrame) -> None:
    if "prior_mode" in frame.columns:
        modes = frame["prior_mode"]
        if modes.isna().any() or modes.nunique() != 1 or not modes.isin(["legacy", "matched_full"]).all():
            raise ValueError("Require exactly one explicit non-null prior mode")
    # Files without a mode column are supported as historical legacy files.
    required = {"budget", "strategy", "benchmark_seed", *METRICS}
    if not required.issubset(frame.columns):
        raise ValueError(f"Missing columns: {sorted(required - set(frame.columns))}")
    paired = frame[frame["strategy"].isin(["policy_active", "passive_characterisation"])]
    if paired.empty or paired[["budget", "benchmark_seed"]].isna().any().any():
        raise ValueError("Paired data must have non-null budget and world keys")
    if paired.duplicated(["budget", "strategy", "benchmark_seed"]).any():
        raise ValueError("Duplicate world/strategy/budget rows")
    if not np.isfinite(paired[list(METRICS)].to_numpy(dtype=float)).all():
        raise ValueError("Paired metrics must be finite")
    for budget in frame["budget"].unique():
        group = paired[paired["budget"] == budget]
        active = set(group.loc[group["strategy"] == "policy_active", "benchmark_seed"])
        passive = set(group.loc[group["strategy"] == "passive_characterisation", "benchmark_seed"])
        if not active or active != passive:
            raise ValueError(f"Unmatched world pairs at budget {budget}")


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

    if args.bootstrap_samples < 1 or args.permutation_samples < 1:
        raise ValueError("Resampling counts must be positive")
    frame = pd.read_csv(args.input)
    validate_pairs(frame)
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
                "prior_mode": frame["prior_mode"].iloc[0] if "prior_mode" in frame else "legacy",
                "better_direction": "lower" if metric in {"false_positive_rate", "effect_mae"} else "higher",
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
