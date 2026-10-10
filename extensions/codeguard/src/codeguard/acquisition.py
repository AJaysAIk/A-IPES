"""Selectors receive public candidate metadata and queried feedback only."""

import math
from dataclasses import dataclass

import numpy as np
from scipy.special import betainc, digamma


@dataclass(frozen=True)
class Candidate:
    sample_id: str
    cell: str
    family: str


def entropy(p):
    if p <= 0 or p >= 1:
        return 0.0
    return -p * math.log(p) - (1 - p) * math.log1p(-p)


def information(a, b):
    p = a / (a + b)
    expected = digamma(a + b + 1) - (a * digamma(a + 1) + b * digamma(b + 1)) / (a + b)
    outcome = max(0.0, entropy(p) - expected)
    q = betainc(a, b, 0.8)
    policy = max(
        0.0,
        entropy(q)
        - p * entropy(betainc(a + 1, b, 0.8))
        - (1 - p) * entropy(betainc(a, b + 1, 0.8)),
    )
    return outcome, policy


def run(candidates, query, strategy, budgets, seed):
    if strategy not in (
        "random",
        "fixed",
        "outcome_only",
        "policy_only",
        "full",
        "no_policy",
        "no_boundary",
        "no_novelty",
    ):
        raise ValueError(strategy)
    if len({c.sample_id for c in candidates}) != len(candidates):
        raise ValueError("duplicate candidate")
    if max(budgets) > len(candidates):
        raise ValueError("budget exceeds pool")
    rng = np.random.default_rng(seed)
    cells = sorted({c.cell for c in candidates})
    posterior = {cell: [1.0, 1.0] for cell in cells}
    remaining = list(candidates)
    seen = set()
    trace = []
    snapshots = {}
    order = rng.permutation(len(candidates))
    rank = {candidates[i].sample_id: j for j, i in enumerate(order)}
    for t in range(1, max(budgets) + 1):
        if strategy == "random":
            chosen = remaining[int(rng.integers(len(remaining)))]
            components = None
        elif strategy == "fixed":
            available = [c for c in remaining if c.cell == cells[(t - 1) % len(cells)]]
            if not available:
                available = remaining
            chosen = min(available, key=lambda c: rank[c.sample_id])
            components = None
        else:
            matrix = []
            for c in remaining:
                a, b = posterior[c.cell]
                oi, pi = information(a, b)
                matrix.append(
                    [oi, pi, max(0.0, 1 - abs(a / (a + b) - 0.8)), float(c.family not in seen)]
                )
            raw = np.array(matrix)
            den = raw.max(axis=0)
            norm = raw / np.where(den > 0, den, 1)
            weights = {
                "full": [1, 1.5, 0.2, 0.1],
                "no_policy": [1, 0, 0.2, 0.1],
                "no_boundary": [1, 1.5, 0, 0.1],
                "no_novelty": [1, 1.5, 0.2, 0],
                "outcome_only": [1, 0, 0, 0],
                "policy_only": [0, 1, 0, 0],
            }[strategy]
            scores = norm @ np.array(weights)
            ix = min(
                range(len(remaining)),
                key=lambda j: (-round(scores[j], 12), rank[remaining[j].sample_id]),
            )
            chosen = remaining[ix]
            components = {"normalised": norm[ix].tolist(), "score": float(scores[ix])}
        outcome = query(chosen.sample_id)
        if type(outcome) not in (bool, int) or outcome not in (0, 1):
            raise ValueError("feedback must be binary correctness")
        posterior[chosen.cell][0 if outcome else 1] += 1
        seen.add(chosen.family)
        remaining.remove(chosen)
        trace.append(
            dict(
                step=t,
                sample_id=chosen.sample_id,
                cell=chosen.cell,
                family=chosen.family,
                correct=bool(outcome),
                acquisition=components,
            )
        )
        if t in budgets:
            snapshots[t] = {cell: a / (a + b) for cell, (a, b) in posterior.items()}
    return snapshots, trace
