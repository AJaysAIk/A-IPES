from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


FULL_STRATEGY = "policy_active_full"

METRICS = (
    "attack_recall",
    "balanced_accuracy",
    "effect_mae",
    "false_positive_rate",
    "policy_exact_match",
    "shifted_attack_recall",
    "posterior_reduction_ratio",
    "information_gain_bits",
)


def paired_bootstrap_ci(
    differences: np.ndarray,
    rng: np.random.Generator,
    repetitions: int = 20_000,
) -> tuple[float, float]:
    if len(differences) == 0:
        return np.nan, np.nan

    indices = rng.integers(
        0,
        len(differences),
        size=(repetitions, len(differences)),
    )
    bootstrap_means = differences[indices].mean(axis=1)

    return (
        float(np.quantile(bootstrap_means, 0.025)),
        float(np.quantile(bootstrap_means, 0.975)),
    )


def sign_flip_pvalue(
    differences: np.ndarray,
    rng: np.random.Generator,
    repetitions: int = 20_000,
) -> float:
    if len(differences) == 0:
        return np.nan

    observed = abs(float(differences.mean()))
    signs = rng.choice(
        np.array([-1.0, 1.0]),
        size=(repetitions, len(differences)),
    )
    null_means = np.abs((signs * differences).mean(axis=1))

    return float(
        (np.count_nonzero(null_means >= observed) + 1)
        / (repetitions + 1)
    )


def analyse(
    frame: pd.DataFrame,
    random_seed: int = 2026,
) -> pd.DataFrame:
    rng = np.random.default_rng(random_seed)
    rows: list[dict] = []

    variants = sorted(
        strategy
        for strategy in frame["strategy"].unique()
        if strategy not in {
            FULL_STRATEGY,
            "passive_characterisation",
        }
    )

    for budget in sorted(frame["budget"].unique()):
        budget_frame = frame[frame["budget"] == budget]

        full = budget_frame[
            budget_frame["strategy"] == FULL_STRATEGY
        ].set_index("benchmark_seed")

        for variant in variants:
            ablated = budget_frame[
                budget_frame["strategy"] == variant
            ].set_index("benchmark_seed")

            shared = full.index.intersection(ablated.index)

            for metric in METRICS:
                full_values = full.loc[shared, metric].astype(float)
                ablated_values = ablated.loc[shared, metric].astype(float)

                valid = full_values.notna() & ablated_values.notna()
                full_values = full_values[valid]
                ablated_values = ablated_values[valid]

                # Positive means the full method has a larger value.
                differences = (
                    full_values.to_numpy()
                    - ablated_values.to_numpy()
                )

                ci_low, ci_high = paired_bootstrap_ci(
                    differences,
                    rng,
                )
                pvalue = sign_flip_pvalue(differences, rng)

                rows.append(
                    {
                        "budget": int(budget),
                        "variant": variant,
                        "metric": metric,
                        "n_benchmarks": len(differences),
                        "full_mean": float(full_values.mean()),
                        "ablated_mean": float(ablated_values.mean()),
                        "mean_difference_full_minus_ablated": (
                            float(differences.mean())
                        ),
                        "ci95_low": ci_low,
                        "ci95_high": ci_high,
                        "sign_flip_pvalue": pvalue,
                    }
                )

    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Paired analysis of A-IPES acquisition ablations."
    )
    parser.add_argument(
        "--input",
        default="results/acquisition_ablation_30/per_benchmark.csv",
    )
    parser.add_argument(
        "--output",
        default="results/acquisition_ablation_30/"
        "paired_full_vs_ablated.csv",
    )
    parser.add_argument("--random-seed", type=int, default=2026)
    args = parser.parse_args()

    frame = pd.read_csv(args.input)
    result = analyse(frame, random_seed=args.random_seed)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False)

    print(result.to_string(index=False))
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()
