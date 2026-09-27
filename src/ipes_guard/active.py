from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import List, Sequence

import numpy as np
from sklearn.tree import DecisionTreeRegressor

from .domain import PolicyState
from .signature import EffectModel, fit_effect_model
from .tooling import ToolSpec


@dataclass(frozen=True)
class ActiveProbeResult:
    selected_states: tuple[PolicyState, ...]
    effect_model: EffectModel
    scores: tuple[float, ...]


def candidate_policy_states() -> List[PolicyState]:
    """Enumerate a compact state pool, including the resource boundary."""
    states: List[PolicyState] = []
    for bits in product([0.0, 1.0], repeat=5):
        # Exclude logically impossible evidence_verified=1 with no evidence_present.
        if bits[1] > bits[0]:
            continue
        for resource in (0.0, 5.0):
            states.append(PolicyState(*bits, resource))
    return states


def _boundary_score(state: PolicyState) -> float:
    """Prioritise states around policy prerequisite boundaries."""
    score = 0.0
    if state.evidence_present and not state.evidence_verified:
        score += 1.0
    if state.evidence_verified and not state.supplier_approved:
        score += 1.0
    if state.supplier_approved and not state.purchase_authorised:
        score += 1.0
    if state.resource_calls == 5:
        score += 1.0
    return score


def _novelty_score(state: PolicyState, observed: Sequence[PolicyState]) -> float:
    if not observed:
        return 1.0
    distances = [np.linalg.norm(state.to_vector() - other.to_vector()) for other in observed]
    return float(min(distances) / np.sqrt(len(state.to_vector())))


def _ensemble_disagreement(
    tool: ToolSpec,
    observed: Sequence[PolicyState],
    candidate: PolicyState,
    ensemble_size: int,
    random_state: int,
) -> float:
    if len(observed) < 2:
        return 0.0

    rng = np.random.default_rng(random_state)
    x = np.vstack([state.to_vector() for state in observed])
    y = np.vstack([tool.apply(state, {}).to_vector() for state in observed])
    predictions = []
    for idx in range(ensemble_size):
        sample_idx = rng.integers(0, len(observed), size=len(observed))
        model = DecisionTreeRegressor(max_depth=6, random_state=random_state + idx)
        model.fit(x[sample_idx], y[sample_idx])
        predictions.append(model.predict(candidate.to_vector().reshape(1, -1))[0])
    matrix = np.vstack(predictions)
    return float(np.mean(np.var(matrix, axis=0)))


def select_active_probes(
    tool: ToolSpec,
    budget: int = 6,
    candidates: Sequence[PolicyState] | None = None,
    ensemble_size: int = 12,
    random_state: int = 0,
) -> ActiveProbeResult:
    """Policy-aware active intervention selection.

    At each iteration, choose the unobserved state with the largest combination of:
    1) ensemble disagreement about the tool's post-state;
    2) proximity to a policy prerequisite boundary;
    3) diversity from already selected states.

    The simulator's ToolSpec.apply is the intervention oracle in this prototype.
    """
    pool = list(candidates or candidate_policy_states())
    if budget < 1 or budget > len(pool):
        raise ValueError("budget must be between 1 and the number of candidate states")

    selected: List[PolicyState] = []
    selected_scores: List[float] = []

    for step in range(budget):
        best_state = None
        best_score = -np.inf
        for candidate in pool:
            if candidate in selected:
                continue
            disagreement = _ensemble_disagreement(
                tool,
                selected,
                candidate,
                ensemble_size=ensemble_size,
                random_state=random_state + step * 101,
            )
            score = disagreement + 0.35 * _boundary_score(candidate) + 0.15 * _novelty_score(candidate, selected)
            if score > best_score:
                best_score = score
                best_state = candidate
        assert best_state is not None
        selected.append(best_state)
        selected_scores.append(float(best_score))

    model = fit_effect_model(tool, selected)
    return ActiveProbeResult(tuple(selected), model, tuple(selected_scores))
