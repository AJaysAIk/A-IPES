"""v0.5: bounded temporal acquisition with observable counterexample validation."""

from __future__ import annotations

import random
from collections import Counter
from dataclasses import dataclass
from itertools import product
from math import log2

ACTIONS = ("grant", "revoke", "use", "idle")
STRATEGIES = (
    "specification_active",
    "transition_active",
    "counterexample_guided",
    "random",
)
TRACE_LENGTH = 4
SPECIFICATION_WEIGHT = 2.0
Trace = tuple[str, ...]
Response = tuple[tuple[bool, bool], ...]  # accepted use, irrelevant pulse


@dataclass(frozen=True)
class TemporalModel:
    early: bool
    stale: bool
    pulse: bool

    @property
    def name(self) -> str:
        kind = (
            "both"
            if self.early and self.stale
            else ("early" if self.early else "stale" if self.stale else "safe")
        )
        return f"{kind}_pulse{int(self.pulse)}"

    def execute(self, trace: Trace) -> Response:
        valid = ever_granted = False
        responses = []
        for action in trace:
            if action not in ACTIONS:
                raise ValueError(f"unknown action: {action}")
            accepted = False
            if action == "grant":
                valid = ever_granted = True
            elif action == "revoke":
                valid = False
            elif action == "use":
                accepted = (
                    valid
                    or (self.early and not ever_granted)
                    or (self.stale and ever_granted)
                )
            responses.append((accepted, self.pulse and action == "idle"))
        return tuple(responses)


def library() -> tuple[TemporalModel, ...]:
    return tuple(TemporalModel(*bits) for bits in product((False, True), repeat=3))


def candidate_traces() -> tuple[Trace, ...]:
    return tuple(product(ACTIONS, repeat=TRACE_LENGTH))


def monitor(trace: Trace, responses: Response) -> bool:
    """Read only public actions and responses; never inspect model switches."""
    if len(trace) != len(responses):
        raise ValueError("trace/response length mismatch")
    valid = False
    violation = False
    for action, (accepted, _pulse) in zip(trace, responses):
        if action not in ACTIONS:
            raise ValueError(f"unknown action: {action}")
        if action == "use" and accepted and not valid:
            violation = True
        if action == "grant":
            valid = True
        elif action == "revoke":
            valid = False
    return violation


def entropy(labels) -> float:
    counts = Counter(labels)
    total = sum(counts.values())
    return -sum((n / total) * log2(n / total) for n in counts.values())


def refine(posterior, trace: Trace, response: Response) -> tuple[TemporalModel, ...]:
    remaining = tuple(model for model in posterior if model.execute(trace) == response)
    if not remaining:
        raise ValueError("observed tool is outside the temporal hypothesis class")
    return remaining


def select_trace(strategy, remaining, posterior, predictions, violations):
    """No actual world or truth label is accessible to acquisition."""
    if strategy == "random":
        return remaining[0]
    if strategy == "counterexample_guided":
        for model in posterior:
            for trace in remaining:
                if violations[model, trace]:
                    return trace
        return remaining[0]
    if strategy not in ("specification_active", "transition_active"):
        raise ValueError(f"unknown strategy: {strategy}")

    def score(trace):
        response_information = entropy(predictions[m, trace] for m in posterior)
        spec_information = entropy(violations[m, trace] for m in posterior)
        return response_information + (
            SPECIFICATION_WEIGHT * spec_information
            if strategy == "specification_active"
            else 0
        )

    # max preserves the seeded candidate order on exact ties.
    return max(remaining, key=score)


def run_temporal(budgets=(1, 2, 4, 8), seeds=tuple(range(20))):
    budgets = tuple(sorted(set(budgets)))
    pool = candidate_traces()
    if not budgets or any(
        not isinstance(b, int) or b < 1 or b > len(pool) for b in budgets
    ):
        raise ValueError("budgets must be integer trace counts in 1..256")
    models = library()
    predictions = {(m, t): m.execute(t) for m in models for t in pool}
    violations = {(m, t): monitor(t, predictions[m, t]) for m in models for t in pool}
    rows, audits = [], []
    for seed in seeds:
        order = list(pool)
        random.Random(int(seed)).shuffle(order)
        for world in models:
            unsafe = any(violations[world, trace] for trace in pool)
            for strategy in STRATEGIES:
                remaining = list(order)
                posterior = models
                first = None
                for query in range(1, max(budgets) + 1):
                    trace = select_trace(
                        strategy, remaining, posterior, predictions, violations
                    )
                    response = world.execute(trace)  # only actual black-box query
                    observed_violation = monitor(trace, response)
                    size_before = len(posterior)
                    posterior = refine(posterior, trace, response)
                    remaining.remove(trace)
                    if observed_violation and first is None:
                        first = query
                    audits.append(
                        {
                            "world": world.name,
                            "strategy": strategy,
                            "seed": int(seed),
                            "query": query,
                            "trace": trace,
                            "response": response,
                            "violation": observed_violation,
                            "posterior_before": size_before,
                            "posterior_after": len(posterior),
                            "action_calls": query * TRACE_LENGTH,
                            "resets": query,
                        }
                    )
                    if query in budgets:
                        rows.append(
                            {
                                "world": world.name,
                                "unsafe_world": unsafe,
                                "strategy": strategy,
                                "seed": int(seed),
                                "budget": query,
                                "action_calls": query * TRACE_LENGTH,
                                "resets": query,
                                "violation_detected": first is not None,
                                "first_violation_query": first,
                                "first_violation_calls": None
                                if first is None
                                else first * TRACE_LENGTH,
                            }
                        )
    return rows, audits
