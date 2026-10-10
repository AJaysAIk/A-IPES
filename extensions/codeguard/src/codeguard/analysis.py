"""Descriptive and paired analysis; no test-driven tuning of acquisition."""

import csv
import hashlib
import json
import time
from pathlib import Path

import numpy as np

from .acquisition import Candidate, run
from .corpus import CLASSES, TRANSFORMS, load

STRATEGIES = (
    "random",
    "fixed",
    "outcome_only",
    "policy_only",
    "full",
    "no_policy",
    "no_boundary",
    "no_novelty",
)
BUDGETS = (6, 12, 24, 48)


def confusion(truth, pred):
    if len(truth) != len(pred):
        raise ValueError("unaligned outcomes")
    tp = sum(t and p for t, p in zip(truth, pred))
    fn = sum(t and not p for t, p in zip(truth, pred))
    fp = sum(not t and p for t, p in zip(truth, pred))
    tn = sum(not t and not p for t, p in zip(truth, pred))
    return dict(
        tp=int(tp),
        fn=int(fn),
        fp=int(fp),
        tn=int(tn),
        recall=tp / (tp + fn) if tp + fn else None,
        precision=tp / (tp + fp) if tp + fp else None,
        fpr=fp / (fp + tn) if fp + tn else None,
        f1=2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None,
    )


def summary(rows, results):
    valid = [r for r in rows if results[r["sample_id"]]["status"] == "ok"]
    truth = []
    pred = []
    for row in valid:
        for c in CLASSES:
            truth.append(row["vulnerable"] and row["category"] == c)
            pred.append(results[row["sample_id"]]["predictions"][c])
    target = confusion(
        [r["vulnerable"] for r in valid],
        [results[r["sample_id"]]["predictions"][r["category"]] for r in valid],
    )
    per = {}
    for c in CLASSES:
        group = [r for r in valid if r["category"] == c]
        per[c] = confusion(
            [r["vulnerable"] for r in group],
            [results[r["sample_id"]]["predictions"][c] for r in group],
        )
    return dict(
        samples=len(rows),
        valid=len(valid),
        coverage=len(valid) / len(rows),
        target_class=target,
        micro_all_classes=confusion(truth, pred),
        per_class=per,
    )


def cluster_interval(values, seed=42, n=10000):
    arr = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    sampled = rng.choice(arr, size=(n, len(arr)), replace=True).mean(axis=1)
    return {
        "mean": float(arr.mean()),
        "ci95": [float(x) for x in np.quantile(sampled, [0.025, 0.975])],
        "clusters": len(arr),
        "method": "paired family cluster bootstrap; selection seeds averaged within family",
    }


def analyse(manifest):
    root = Path(manifest).parent.parent
    rows = load(manifest)
    outputs = [json.loads(line) for line in (root / "results/model.jsonl").read_text().splitlines()]
    if len(outputs) != len(rows) or len({r["sample_id"] for r in outputs}) != len(rows):
        raise ValueError("model run incomplete/duplicate")
    model = {r["sample_id"]: r for r in outputs}
    static_data = json.loads((root / "results/static.json").read_text())
    static = {r["sample_id"]: r for r in static_data["results"]}
    ids = {r["sample_id"] for r in rows}
    if set(model) != ids or set(static) != ids:
        raise ValueError("result ID mismatch")
    corpus_hash = hashlib.sha256(Path(manifest).read_bytes()).hexdigest()
    meta = json.loads((root / "results/model.meta.json").read_text())
    if meta["corpus_sha256"] != corpus_hash or static_data["corpus_sha256"] != corpus_hash:
        raise ValueError("corpus mismatch")
    hybrid = {}
    for sid in ids:
        if model[sid]["status"] != "ok":
            hybrid[sid] = {"status": "escalate", "predictions": None}
        else:
            hybrid[sid] = {
                "status": "ok",
                "predictions": {
                    c: model[sid]["predictions"][c] or static[sid]["predictions"][c]
                    for c in CLASSES
                },
            }
    test = [r for r in rows if r["split"] == "test"]
    dev = [r for r in rows if r["split"] == "development"]
    metrics = {
        split: {
            name: summary(group, out)
            for name, out in [("model", model), ("semgrep", static), ("hybrid", hybrid)]
        }
        for split, group in [("development", dev), ("test", test)]
    }
    robustness = []
    for c in CLASSES:
        for kind in TRANSFORMS:
            group = [r for r in test if r["category"] == c and r["transformation"] == kind]
            sm = summary(group, model)
            originals = {
                (r["family"], r["vulnerable"]): r for r in test if r["transformation"] == "original"
            }
            eligible = misses = 0
            for r in group:
                orig = originals[(r["family"], r["vulnerable"])]
                a = model[orig["sample_id"]]
                b = model[r["sample_id"]]
                if (
                    r["vulnerable"]
                    and a["status"] == "ok"
                    and b["status"] == "ok"
                    and a["predictions"][c]
                ):
                    eligible += 1
                    misses += not b["predictions"][c]
            robustness.append(
                dict(
                    category=c,
                    transformation=kind,
                    **sm["target_class"],
                    evasion_eligible=eligible,
                    evasion_misses=misses,
                    conditional_evasion=misses / eligible if eligible else None,
                )
            )

    # Invalid outputs mean operationally incorrect for profile learning, not clean reviews.
    def correct(r):
        out = model[r["sample_id"]]
        return out["status"] == "ok" and out["predictions"][r["category"]] == r["vulnerable"]

    labels = {r["sample_id"]: bool(correct(r)) for r in dev}
    candidates = [
        Candidate(r["sample_id"], r["category"] + "/" + r["transformation"], r["family"])
        for r in dev
    ]
    family_order = sorted({r["family"] for r in test})
    family_losses = {}
    acq_rows = []
    traces = []
    start = time.perf_counter()
    for strategy in STRATEGIES:
        for seed in range(100):
            snapshots, trace = run(candidates, labels.__getitem__, strategy, BUDGETS, seed)
            if seed == 0:
                traces.append({"strategy": strategy, "seed": seed, "trace": trace})
            for budget, probs in snapshots.items():
                losses = {f: [] for f in family_order}
                for r in test:
                    prob = probs[r["category"] + "/" + r["transformation"]]
                    losses[r["family"]].append((prob - int(correct(r))) ** 2)
                fvalues = [float(np.mean(losses[f])) for f in family_order]
                family_losses.setdefault((strategy, budget), []).append(fvalues)
                prefix = trace[:budget]
                acq_rows.append(
                    dict(
                        strategy=strategy,
                        seed=seed,
                        budget=budget,
                        brier=float(np.mean(fvalues)),
                        failing_families=len({r["family"] for r in prefix if not r["correct"]}),
                        failures=sum(not r["correct"] for r in prefix),
                        cells=len({r["cell"] for r in prefix}),
                    )
                )
    replay_seconds = time.perf_counter() - start
    with (root / "results/acquisition.csv").open("w") as f:
        w = csv.DictWriter(f, fieldnames=list(acq_rows[0]))
        w.writeheader()
        w.writerows(acq_rows)
    (root / "results/selected_probes_seed0.json").write_text(json.dumps(traces, indent=2))
    acq_summary = []
    for strategy in STRATEGIES:
        for budget in BUDGETS:
            selected = [r for r in acq_rows if r["strategy"] == strategy and r["budget"] == budget]
            acq_summary.append(
                dict(
                    strategy=strategy,
                    budget=budget,
                    brier=float(np.mean([r["brier"] for r in selected])),
                    brier_seed_sd=float(np.std([r["brier"] for r in selected], ddof=1)),
                    failing_families=float(np.mean([r["failing_families"] for r in selected])),
                    cells=float(np.mean([r["cells"] for r in selected])),
                )
            )
    difference = np.mean(family_losses[("full", 24)], axis=0) - np.mean(
        family_losses[("fixed", 24)], axis=0
    )
    recall_diffs = []
    fpr_diffs = []
    for family in family_order:
        positives = [r for r in test if r["family"] == family and r["vulnerable"]]
        negatives = [r for r in test if r["family"] == family and not r["vulnerable"]]

        def delta(group):
            return np.mean(
                [
                    int(hybrid[r["sample_id"]]["predictions"][r["category"]])
                    - int(model[r["sample_id"]]["predictions"][r["category"]])
                    for r in group
                    if hybrid[r["sample_id"]]["status"] == "ok"
                ]
            )

        recall_diffs.append(delta(positives))
        fpr_diffs.append(delta(negatives))
    report = {
        "metrics": metrics,
        "robustness": robustness,
        "acquisition": acq_summary,
        "full_minus_fixed_brier_B24": cluster_interval(difference),
        "hybrid_minus_model_recall": cluster_interval(recall_diffs),
        "hybrid_minus_model_fpr": cluster_interval(fpr_diffs),
        "cost": {
            "model_calls": len(outputs),
            "model_seconds": sum(r["latency_s"] for r in outputs),
            "model_p50_s": float(np.median([r["latency_s"] for r in outputs])),
            "model_p95_s": float(np.quantile([r["latency_s"] for r in outputs], 0.95)),
            "input_tokens": sum(r["prompt_tokens"] for r in outputs),
            "output_tokens": sum(r["generation_tokens"] or 0 for r in outputs),
            "static_batch_seconds": static_data["batch_seconds"],
            "hybrid_sequential_estimated_seconds": sum(r["latency_s"] for r in outputs)
            + static_data["batch_seconds"],
            "acquisition_replay_seconds": replay_seconds,
        },
        "limitations": [
            "Single small quantised model, handcrafted templates, no external annotation.",
            "Selection seeds are not independent scientific replicates.",
            "Held-out family bootstrap only nine clusters, conditional on fixed development pool.",
            "Model frozen; source text reviewed, no tool-using agent or malicious execution.",
            "Synthetic family variants may share structural shortcuts; no real-project generalisation.",  # noqa: E501
            "Hybrid cost is sequential estimate, not independently timed pipeline.",
        ],
    }
    (root / "results/summary.json").write_text(json.dumps(report, indent=2))
    plot(root, report)
    print(
        json.dumps(
            {
                "test": metrics["test"],
                "brier_difference": report["full_minus_fixed_brier_B24"],
                "cost": report["cost"],
            },
            indent=2,
        )
    )


def plot(root, report):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {"font.size": 10, "figure.dpi": 160, "axes.spines.top": False, "axes.spines.right": False}
    )
    fig, ax = plt.subplots(figsize=(7, 4))
    for strategy in ("random", "fixed", "full", "outcome_only"):
        vals = [r for r in report["acquisition"] if r["strategy"] == strategy]
        ax.plot([r["budget"] for r in vals], [r["brier"] for r in vals], marker="o", label=strategy)
    ax.set(
        xlabel="Replay query budget (cached development outcomes)",
        ylabel="Held-out Brier score (lower is better)",
        title="CodeGuard: profile learning, one fixed local model",
    )
    ax.legend()
    fig.tight_layout()
    fig.savefig(root / "figures/acquisition.png")
    plt.close(fig)
    fig, axs = plt.subplots(1, 2, figsize=(8, 4))
    names = ["model", "semgrep", "hybrid"]
    for ax, metric, title in zip(
        axs, ["recall", "fpr"], ["Vulnerability recall", "Safe-case false-positive rate"]
    ):
        vals = [report["metrics"]["test"][n]["target_class"][metric] for n in names]
        ax.bar(names, vals, color=["#4477aa", "#999999", "#228866"])
        ax.set_ylim(0, 1)
        ax.set_title(title)
        for i, v in enumerate(vals):
            ax.text(i, v + 0.025, f"{v:.1%}", ha="center")
    fig.suptitle("Held-out pilot: 36 vulnerable + 36 safe variants; 9 families")
    fig.tight_layout()
    fig.savefig(root / "figures/defence.png")
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 3))
    matrix = np.array(
        [
            [
                next(
                    r["recall"]
                    for r in report["robustness"]
                    if r["category"] == c and r["transformation"] == t
                )
                for t in TRANSFORMS
            ]
            for c in CLASSES
        ]
    )
    im = ax.imshow(matrix, vmin=0, vmax=1, cmap="Blues")
    ax.set_xticks(range(4), TRANSFORMS)
    ax.set_yticks(range(3), CLASSES)
    for i in range(3):
        for j in range(4):
            ax.text(
                j,
                i,
                f"{matrix[i, j]:.0%}",
                ha="center",
                va="center",
                color="white" if matrix[i, j] > 0.6 else "black",
            )
    ax.set_title("Local-model recall: three held-out positives per cell")
    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    fig.savefig(root / "figures/robustness.png")
    plt.close(fig)
