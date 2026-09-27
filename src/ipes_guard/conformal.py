from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class ConformalRadius:
    """Simple split-conformal max-residual radius for state-vector prediction."""

    alpha: float
    radius: float

    def interval(self, prediction: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        lower = prediction - self.radius
        upper = prediction + self.radius
        return lower, upper


def fit_conformal_radius(
    predictions: np.ndarray,
    targets: np.ndarray,
    alpha: float = 0.1,
) -> ConformalRadius:
    if predictions.shape != targets.shape:
        raise ValueError("Predictions and targets must have the same shape.")
    if len(predictions) == 0:
        raise ValueError("Calibration data is empty.")
    scores = np.max(np.abs(predictions - targets), axis=1)
    n = len(scores)
    quantile = min(1.0, np.ceil((n + 1) * (1 - alpha)) / n)
    radius = float(np.quantile(scores, quantile, method="higher"))
    return ConformalRadius(alpha=alpha, radius=radius)
