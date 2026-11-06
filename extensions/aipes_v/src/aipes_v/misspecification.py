"""Frozen v0.6: separate observed safety violations from model inadequacy."""

from __future__ import annotations

import random
from collections import Counter
from dataclasses import dataclass
from itertools import product
from math import fsum, log2

from .temporal import ACTIONS, STRATEGIES, Response, Trace, library

TRACE_LENGTH = 6
LEASE_AGE = 2
SPECIFICATION_WEIGHT = 2.0


@dataclass(frozen=True)
class LeaseWorld:
    kind: str
    pulse: bool

    @property
    def name(self):
        return f"{self.kind}_pulse{int(self.pulse)}"

    def execute(self, trace: Trace) -> Response:
        ttl = {
            "compliant": 2,
            "premature": 1,
            "late": 3,
            "ignores_expiry": None,
            "early": 2,
            "stale": 2,
        }[self.kind]
        age = None
        revoked = False
        result = []
        for action in trace:
            if action not in ACTIONS:
                raise ValueError(f"unknown action: {action}")
            if action == "grant":
                age = 0
                revoked = False
            else:
                if age is not None:
                    age += 1
                if action == "revoke" and self.kind != "stale":
                    revoked = True
            accepted = action == "use" and (
                (age is not None and not revoked and (ttl is None or age <= ttl))
                or (self.kind == "early" and age is None)
            )
            result.append((accepted, self.pulse and action == "idle"))
        return tuple(result)


def lease_monitor(trace: Trace, response: Response) -> bool:
    """Public-history monitor independent of the world's clock implementation."""
    if len(trace) != len(response):
        raise ValueError("trace/response length mismatch")
    last_grant = None
    revoked = False
    violation = False
    for index, (action, (accepted, _pulse)) in enumerate(zip(trace, response)):
        if action not in ACTIONS:
            raise ValueError(f"unknown action: {action}")
        if action == "grant":
            last_grant = index
            revoked = False
        elif action == "revoke":
            revoked = True
        elif action == "use" and accepted:
            violation |= last_grant is None or revoked or index - last_grant > LEASE_AGE
    return bool(violation)


def worlds():
    kinds = ("compliant", "premature", "late", "ignores_expiry", "early", "stale")
    return tuple(LeaseWorld(k, pulse) for k in kinds for pulse in (False, True))


def model_order(seed):
    order = list(range(len(library())))
    random.Random(int(seed) + 1000003).shuffle(order)
    return tuple(order)


def stable_entropy(labels):
    counts = Counter(labels)
    total = sum(counts.values())
    return -fsum((n / total) * log2(n / total) for n in sorted(counts.values()))


def outcome_status(violation_seen, model_inadequate):
    if violation_seen:
        return "violation_observed"
    if model_inadequate:
        return "model_inadequate_without_violation"
    return "no_counterexample_observed"


class LeaseExperiment:
    def __init__(self):
        self.pool = tuple(product(ACTIONS, repeat=TRACE_LENGTH))
        self.models = library()
        self.predictions = tuple(
            tuple(m.execute(t) for t in self.pool) for m in self.models
        )
        self.violations = tuple(
            tuple(lease_monitor(t, r) for t, r in zip(self.pool, rs))
            for rs in self.predictions
        )
        # Finite exhaustive oracle is only for evaluation labels, not acquisition.
        self.oracle = []
        for world in worlds():
            responses = tuple(world.execute(t) for t in self.pool)
            equivalent = [
                m.name
                for m, rs in zip(self.models, self.predictions)
                if rs == responses
            ]
            unsafe = any(lease_monitor(t, r) for t, r in zip(self.pool, responses))
            expected_unsafe = world.kind not in ("compliant", "premature")
            expected_in_class = world.kind == "ignores_expiry"
            if unsafe != expected_unsafe or bool(equivalent) != expected_in_class:
                raise AssertionError(
                    f"world label failed exhaustive check: {world.name}"
                )
            self.oracle.append(
                {
                    "world": world.name,
                    "unsafe_world": unsafe,
                    "out_of_class": not bool(equivalent),
                    "equivalent_models": equivalent,
                    "traces_checked": len(self.pool),
                }
            )
        self._score_cache = {}

    def scores(self, strategy, posterior):
        key = strategy, tuple(sorted(posterior))
        if key not in self._score_cache:
            weight = SPECIFICATION_WEIGHT if strategy == "specification_active" else 0
            self._score_cache[key] = tuple(
                stable_entropy(self.predictions[m][t] for m in key[1])
                + weight * stable_entropy(self.violations[m][t] for m in key[1])
                for t in range(len(self.pool))
            )
        return self._score_cache[key]

    def choose(self, strategy, remaining, posterior):
        """Selector only receives candidate IDs and the observed version space."""
        work = {
            "candidate_checks": 0,
            "logical_response_lookups": 0,
            "logical_violation_lookups": 0,
        }
        if not posterior or strategy == "random":
            work["candidate_checks"] = 1
            return remaining[0], work
        if strategy == "counterexample_guided":
            for model in posterior:
                for trace in remaining:
                    work["candidate_checks"] += 1
                    work["logical_violation_lookups"] += 1
                    if self.violations[model][trace]:
                        return trace, work
            work["candidate_checks"] += 1
            return remaining[0], work
        if strategy not in ("specification_active", "transition_active"):
            raise ValueError(f"unknown strategy: {strategy}")
        scores = self.scores(strategy, posterior)
        work["candidate_checks"] = len(remaining)
        work["logical_response_lookups"] = len(remaining) * len(posterior)
        if strategy == "specification_active":
            work["logical_violation_lookups"] = len(remaining) * len(posterior)
        return max(remaining, key=lambda trace: scores[trace]), work

    def run(self, budgets=(1, 2, 4, 8), seeds=tuple(range(20))):
        budgets = tuple(sorted(set(budgets)))
        if not budgets or any(
            type(b) is not int or b < 1 or b > len(self.pool) for b in budgets
        ):
            raise ValueError("budgets must be integer trace counts in 1..4096")
        rows, audits = [], []
        for seed in seeds:
            order = list(range(len(self.pool)))
            random.Random(int(seed)).shuffle(order)
            for world, oracle in zip(worlds(), self.oracle):
                for strategy in STRATEGIES:
                    remaining, posterior = list(order), model_order(seed)
                    first_violation = first_mismatch = None
                    cumulative = Counter()
                    for query in range(1, max(budgets) + 1):
                        trace_id, work = self.choose(strategy, remaining, posterior)
                        trace = self.pool[trace_id]
                        response = world.execute(trace)
                        violation = lease_monitor(trace, response)
                        before = len(posterior)
                        posterior = tuple(
                            m
                            for m in posterior
                            if self.predictions[m][trace_id] == response
                        )
                        cumulative.update(work)
                        cumulative["refinement_response_lookups"] += before
                        remaining.remove(trace_id)
                        if violation and first_violation is None:
                            first_violation = query
                        if not posterior and first_mismatch is None:
                            first_mismatch = query
                        audit = {
                            "world": world.name,
                            "strategy": strategy,
                            "seed": int(seed),
                            "query": query,
                            "trace": trace,
                            "response": response,
                            "violation": violation,
                            "posterior_before": before,
                            "posterior_after": len(posterior),
                            "model_inadequate": first_mismatch is not None,
                            "action_calls": query * TRACE_LENGTH,
                            "resets": query,
                            **work,
                            "refinement_response_lookups": before,
                        }
                        audits.append(audit)
                        if query in budgets:
                            rows.append(
                                {
                                    "world": world.name,
                                    "kind": world.kind,
                                    "unsafe_world": oracle["unsafe_world"],
                                    "out_of_class": oracle["out_of_class"],
                                    "strategy": strategy,
                                    "seed": int(seed),
                                    "budget": query,
                                    "action_calls": query * TRACE_LENGTH,
                                    "resets": query,
                                    "violation_detected": first_violation is not None,
                                    "model_inadequate": first_mismatch is not None,
                                    "first_violation_query": first_violation,
                                    "first_violation_calls": None
                                    if first_violation is None
                                    else first_violation * TRACE_LENGTH,
                                    "first_mismatch_query": first_mismatch,
                                    "first_mismatch_calls": None
                                    if first_mismatch is None
                                    else first_mismatch * TRACE_LENGTH,
                                    "status": outcome_status(
                                        first_violation is not None,
                                        first_mismatch is not None,
                                    ),
                                    **dict(cumulative),
                                }
                            )
        return rows, audits
