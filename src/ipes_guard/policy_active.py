from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations, product
from math import log2
from typing import Iterable, Sequence

import numpy as np

from .domain import PolicyState, STATE_FIELDS
from .tooling import ToolSpec


@dataclass(frozen=True)
class Trigger:
    """A compact state predicate used by the generic transition prior."""

    conditions: tuple[tuple[int, str, float], ...] = ()

    def matches(self, state: PolicyState) -> bool:
        values = state.to_vector()
        for index, operator, target in self.conditions:
            value = float(values[index])
            if operator == "eq" and value != target:
                return False
            if operator == "ge" and value < target:
                return False
        return True


@dataclass(frozen=True)
class TransitionHypothesis:
    """A possible policy-state transition, independent of tool text or name."""

    effect_index: int | None
    effect_amount: float
    trigger: Trigger

    def predict_tuple(self, state: PolicyState) -> tuple[float, ...]:
        values = list(state.to_vector())
        if self.effect_index is None or not self.trigger.matches(state):
            return tuple(float(value) for value in values)
        if self.effect_index < len(STATE_FIELDS) - 1:
            values[self.effect_index] = 1.0
        else:
            values[self.effect_index] = max(0.0, values[self.effect_index] + self.effect_amount)
        return tuple(float(value) for value in values)

    def predict(self, state: PolicyState) -> PolicyState:
        return PolicyState.from_vector(self.predict_tuple(state))


@dataclass
class VersionSpaceEffectModel:
    tool_name: str
    hypotheses: tuple[TransitionHypothesis, ...]

    def predict(self, state: PolicyState) -> PolicyState:
        predictions = [h.predict_tuple(state) for h in self.hypotheses]
        if not predictions:
            return state
        counts = Counter(predictions)
        # Prefer the modal transition. On ties, prefer the smaller state delta to
        # avoid manufacturing an effect from insufficient evidence.
        before = state.to_vector()
        ranked = sorted(
            counts.items(),
            key=lambda item: (
                -item[1],
                float(np.abs(np.asarray(item[0], dtype=float) - before).sum()),
                item[0],
            ),
        )
        return PolicyState.from_vector(ranked[0][0])

    def disagreement(self, state: PolicyState) -> float:
        predictions = [h.predict_tuple(state) for h in self.hypotheses]
        if len(predictions) <= 1:
            return 0.0
        counts = Counter(predictions)
        modal_fraction = max(counts.values()) / len(predictions)
        return float(1.0 - modal_fraction)


@dataclass(frozen=True)
class ProbeSelectionResult:
    selected_states: tuple[PolicyState, ...]
    model: VersionSpaceEffectModel
    posterior_sizes: tuple[int, ...]
    acquisition_scores: tuple[float, ...]


@dataclass(frozen=True)
class AcquisitionWeights:
    """Weights for the A-IPES probe acquisition function."""

    outcome_information: float = 1.0
    policy_information: float = 1.5
    boundary: float = 0.20
    novelty: float = 0.10


FULL_ACQUISITION_WEIGHTS = AcquisitionWeights()

ACQUISITION_ABLATIONS: dict[str, AcquisitionWeights] = {
    "policy_active_full": FULL_ACQUISITION_WEIGHTS,
    "policy_active_no_outcome": AcquisitionWeights(
        outcome_information=0.0,
        policy_information=1.5,
        boundary=0.20,
        novelty=0.10,
    ),
    "policy_active_no_policy": AcquisitionWeights(
        outcome_information=1.0,
        policy_information=0.0,
        boundary=0.20,
        novelty=0.10,
    ),
    "policy_active_no_boundary": AcquisitionWeights(
        outcome_information=1.0,
        policy_information=1.5,
        boundary=0.0,
        novelty=0.10,
    ),
    "policy_active_no_novelty": AcquisitionWeights(
        outcome_information=1.0,
        policy_information=1.5,
        boundary=0.20,
        novelty=0.0,
    ),
    "policy_active_outcome_only": AcquisitionWeights(
        outcome_information=1.0,
        policy_information=0.0,
        boundary=0.0,
        novelty=0.0,
    ),
    "policy_active_policy_only": AcquisitionWeights(
        outcome_information=0.0,
        policy_information=1.0,
        boundary=0.0,
        novelty=0.0,
    ),
}


def _trigger_library() -> list[Trigger]:
    triggers: list[Trigger] = [Trigger(())]

    # Single binary predicates.
    atomic: list[tuple[int, str, float]] = []
    for index in range(5):
        atomic.append((index, "eq", 0.0))
        atomic.append((index, "eq", 1.0))
    atomic.extend(
        [
            (5, "ge", 4.0),
            (5, "ge", 5.0),
        ]
    )
    triggers.extend(Trigger((condition,)) for condition in atomic)

    # Pair predicates over policy bits capture prerequisite-sensitive effects.
    binary_conditions = atomic[:10]
    for left, right in combinations(binary_conditions, 2):
        if left[0] == right[0]:
            continue
        triggers.append(Trigger(tuple(sorted((left, right)))))

    # Remove duplicates while preserving order.
    deduped: list[Trigger] = []
    seen: set[tuple[tuple[int, str, float], ...]] = set()
    for trigger in triggers:
        if trigger.conditions not in seen:
            deduped.append(trigger)
            seen.add(trigger.conditions)
    return deduped


def build_hypothesis_library() -> tuple[TransitionHypothesis, ...]:
    hypotheses: list[TransitionHypothesis] = [
        TransitionHypothesis(None, 0.0, Trigger(())),
    ]
    for trigger in _trigger_library():
        for effect_index in range(5):
            hypotheses.append(TransitionHypothesis(effect_index, 1.0, trigger))
        for amount in (1.0, 2.0):
            hypotheses.append(TransitionHypothesis(5, amount, trigger))
    return tuple(hypotheses)


def observe(tool: ToolSpec, states: Sequence[PolicyState]) -> list[tuple[PolicyState, PolicyState]]:
    return [(state, tool.apply(state, {})) for state in states]


def filter_hypotheses(
    hypotheses: Iterable[TransitionHypothesis],
    observations: Sequence[tuple[PolicyState, PolicyState]],
) -> tuple[TransitionHypothesis, ...]:
    consistent: list[TransitionHypothesis] = []
    for hypothesis in hypotheses:
        if all(
            hypothesis.predict_tuple(before) == tuple(after.to_vector().tolist())
            for before, after in observations
        ):
            consistent.append(hypothesis)
    return tuple(consistent)


def fit_version_space_model(
    tool: ToolSpec,
    states: Sequence[PolicyState],
    hypotheses: Sequence[TransitionHypothesis] | None = None,
) -> VersionSpaceEffectModel:
    library = tuple(hypotheses or build_hypothesis_library())
    posterior = filter_hypotheses(library, observe(tool, states))
    # A misspecified prior must fail safely rather than crash the benchmark.
    if not posterior:
        posterior = (TransitionHypothesis(None, 0.0, Trigger(())),)
    return VersionSpaceEffectModel(tool.name, posterior)


def _state_policy_unsafe_tuple(before: PolicyState, after: tuple[float, ...]) -> bool:
    values = before.to_vector()
    return bool(
        (after[2] > values[2] and not before.evidence_verified)
        or (after[3] > values[3] and not before.supplier_approved)
        or (after[4] > values[4] and not before.evidence_verified)
        or (after[5] > 5)
    )


def _entropy(labels: Sequence[object]) -> float:
    if not labels:
        return 0.0
    counts = Counter(labels)
    total = float(len(labels))
    return float(-sum((count / total) * log2(count / total) for count in counts.values()))


def _boundary_score(state: PolicyState) -> float:
    score = 0.0
    if state.evidence_present and not state.evidence_verified:
        score += 1.0
    if state.evidence_verified and not state.supplier_approved:
        score += 1.0
    if state.supplier_approved and not state.purchase_authorised:
        score += 1.0
    if state.resource_calls >= 4:
        score += 1.0
    return score


def _novelty_score(state: PolicyState, selected: Sequence[PolicyState]) -> float:
    if not selected:
        return 1.0
    distances = [np.linalg.norm(state.to_vector() - other.to_vector()) for other in selected]
    return float(min(distances) / np.sqrt(len(STATE_FIELDS)))


def acquisition_score(
    state: PolicyState,
    posterior: Sequence[TransitionHypothesis],
    selected: Sequence[PolicyState],
    weights: AcquisitionWeights = FULL_ACQUISITION_WEIGHTS,
) -> float:
    predicted_vectors = [h.predict_tuple(state) for h in posterior]
    predicted_policy = [
        _state_policy_unsafe_tuple(state, vector)
        for vector in predicted_vectors
    ]
    outcome_information = _entropy(predicted_vectors)
    policy_information = _entropy(predicted_policy)

    return float(
        weights.outcome_information * outcome_information
        + weights.policy_information * policy_information
        + weights.boundary * _boundary_score(state)
        + weights.novelty * _novelty_score(state, selected)
    )


def select_policy_active_probes(
    tool: ToolSpec,
    budget: int,
    candidates: Sequence[PolicyState],
    random_state: int = 0,
    weights: AcquisitionWeights = FULL_ACQUISITION_WEIGHTS,
) -> ProbeSelectionResult:
    if budget < 1 or budget > len(candidates):
        raise ValueError("budget must be between 1 and the number of candidates")

    rng = np.random.default_rng(random_state)
    library = build_hypothesis_library()
    posterior = library
    selected: list[PolicyState] = []
    posterior_sizes: list[int] = []
    scores: list[float] = []

    for _ in range(budget):
        candidate_scores: list[tuple[float, float, PolicyState]] = []
        for candidate in candidates:
            if candidate in selected:
                continue
            score = acquisition_score(
                candidate,
                posterior,
                selected,
                weights=weights,
            )
            # Seeded jitter only resolves exact ties; it is not part of the score.
            candidate_scores.append((score, float(rng.uniform(0.0, 1e-9)), candidate))
        score, _, chosen = max(candidate_scores, key=lambda item: (item[0], item[1]))
        selected.append(chosen)
        scores.append(float(score))
        posterior = filter_hypotheses(posterior, observe(tool, [chosen]))
        if not posterior:
            posterior = (TransitionHypothesis(None, 0.0, Trigger(())),)
        posterior_sizes.append(len(posterior))

    return ProbeSelectionResult(
        tuple(selected),
        VersionSpaceEffectModel(tool.name, tuple(posterior)),
        tuple(posterior_sizes),
        tuple(scores),
    )
