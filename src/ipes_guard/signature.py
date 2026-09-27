from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np
from sklearn.tree import DecisionTreeRegressor

from .domain import PolicyState
from .tooling import ToolSpec


@dataclass
class EffectModel:
    """A per-tool model learned from controlled intervention records."""

    tool_name: str
    regressor: DecisionTreeRegressor

    def predict(self, state: PolicyState) -> PolicyState:
        predicted = self.regressor.predict(state.to_vector().reshape(1, -1))[0]
        return PolicyState.from_vector(predicted)


def fit_effect_model(
    tool: ToolSpec,
    training_states: Sequence[PolicyState],
    argument_sets: Sequence[dict] | None = None,
) -> EffectModel:
    if not training_states:
        raise ValueError("At least one intervention state is required.")
    args = list(argument_sets or [{} for _ in training_states])
    if len(args) != len(training_states):
        raise ValueError("argument_sets must match training_states length.")

    x = np.vstack([s.to_vector() for s in training_states])
    y = np.vstack([tool.apply(s, a).to_vector() for s, a in zip(training_states, args)])
    regressor = DecisionTreeRegressor(random_state=0, max_depth=6)
    regressor.fit(x, y)
    return EffectModel(tool.name, regressor)


def effect_signature(model: EffectModel, probe_states: Sequence[PolicyState]) -> np.ndarray:
    """Concatenate predicted deltas over canonical counterfactual probe states."""
    chunks = []
    for state in probe_states:
        after = model.predict(state)
        chunks.append(state.delta(after))
    return np.concatenate(chunks).astype(float)


def signature_distance(left: np.ndarray, right: np.ndarray) -> float:
    if left.shape != right.shape:
        raise ValueError("Signatures must have identical shape.")
    return float(np.linalg.norm(left - right, ord=2))
