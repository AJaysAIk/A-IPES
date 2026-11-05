from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import log2
from typing import Sequence

import numpy as np

from ipes_guard.domain import PolicyState
from ipes_guard.policy_active import (
    AcquisitionWeights,
    FULL_ACQUISITION_WEIGHTS,
    TransitionHypothesis,
    Trigger,
    VersionSpaceEffectModel,
    acquisition_score,
    build_hypothesis_library,
    filter_hypotheses,
    observe,
)
from ipes_guard.tooling import ToolSpec

from .specs import SafetySpecification, default_specifications, violation_signature, violated_names


@dataclass(frozen=True)
class SpecificationAcquisitionWeights:
    """Weights added to the original A-IPES acquisition objective."""

    base: AcquisitionWeights = FULL_ACQUISITION_WEIGHTS
    specification_information: float = 1.25
    expected_violation: float = 0.35


DEFAULT_SPECIFICATION_WEIGHTS = SpecificationAcquisitionWeights()


@dataclass(frozen=True)
class SpecificationProbeSelectionResult:
    selected_states: tuple[PolicyState, ...]
    model: VersionSpaceEffectModel
    posterior_sizes: tuple[int, ...]
    acquisition_scores: tuple[float, ...]
    diagnostics: tuple[dict, ...]


def _entropy(labels: Sequence[object]) -> float:
    if not labels:
        return 0.0
    counts = Counter(labels)
    total = float(len(labels))
    return float(-sum((count / total) * log2(count / total) for count in counts.values()))


def _predicted_after(state: PolicyState, hypothesis: TransitionHypothesis) -> PolicyState:
    return PolicyState.from_vector(hypothesis.predict_tuple(state))


def specification_information_score(
    state: PolicyState,
    posterior: Sequence[TransitionHypothesis],
    specifications: Sequence[SafetySpecification] | None = None,
) -> float:
    specs = tuple(specifications or default_specifications())
    signatures = [
        violation_signature(state, _predicted_after(state, hypothesis), specs)
        for hypothesis in posterior
    ]
    return _entropy(signatures)


def expected_violation_score(
    state: PolicyState,
    posterior: Sequence[TransitionHypothesis],
    specifications: Sequence[SafetySpecification] | None = None,
) -> float:
    if not posterior:
        return 0.0
    specs = tuple(specifications or default_specifications())
    violating = sum(
        any(violation_signature(state, _predicted_after(state, hypothesis), specs))
        for hypothesis in posterior
    )
    return float(violating / len(posterior))


def specification_aware_score(
    state: PolicyState,
    posterior: Sequence[TransitionHypothesis],
    selected: Sequence[PolicyState],
    specifications: Sequence[SafetySpecification] | None = None,
    weights: SpecificationAcquisitionWeights = DEFAULT_SPECIFICATION_WEIGHTS,
) -> float:
    """Score a probe for policy identification and safety-property evidence."""

    specs = tuple(specifications or default_specifications())
    base = acquisition_score(state, posterior, selected, weights=weights.base)
    spec_information = specification_information_score(state, posterior, specs)
    violation_probability = expected_violation_score(state, posterior, specs)
    return float(
        base
        + weights.specification_information * spec_information
        + weights.expected_violation * violation_probability
    )


def select_specification_aware_probes(
    tool: ToolSpec,
    budget: int,
    candidates: Sequence[PolicyState],
    random_state: int = 0,
    specifications: Sequence[SafetySpecification] | None = None,
    weights: SpecificationAcquisitionWeights = DEFAULT_SPECIFICATION_WEIGHTS,
) -> SpecificationProbeSelectionResult:
    """Select interventions that reduce uncertainty about policy and safety properties."""

    if budget < 1 or budget > len(candidates):
        raise ValueError("budget must be between 1 and the number of candidates")

    specs = tuple(specifications or default_specifications())
    rng = np.random.default_rng(random_state)
    library = build_hypothesis_library()
    posterior = library
    diagnostic_posterior = library
    fallback_used = False

    selected: list[PolicyState] = []
    posterior_sizes: list[int] = []
    scores: list[float] = []
    diagnostics: list[dict] = []

    for probe_index in range(1, budget + 1):
        scored: list[tuple[float, float, PolicyState]] = []
        for candidate in candidates:
            if candidate in selected:
                continue
            score = specification_aware_score(
                candidate,
                posterior,
                selected,
                specifications=specs,
                weights=weights,
            )
            scored.append((score, float(rng.uniform(0.0, 1e-9)), candidate))

        score, _, chosen = max(scored, key=lambda item: (item[0], item[1]))
        selected.append(chosen)
        scores.append(float(score))

        observation = observe(tool, [chosen])
        observed_after = observation[0][1]
        before_count = len(diagnostic_posterior)
        diagnostic_posterior = filter_hypotheses(diagnostic_posterior, observation)
        posterior = filter_hypotheses(posterior, observation)
        step_fallback = not posterior
        fallback_used = fallback_used or step_fallback
        if not posterior:
            posterior = (TransitionHypothesis(None, 0.0, Trigger(())),)

        diagnostics.append(
            {
                "probe_index": probe_index,
                "before": chosen.as_dict(),
                "after": observed_after.as_dict(),
                "acquisition_score": float(score),
                "observed_violations": violated_names(chosen, observed_after, specs),
                "consistent_count_before": before_count,
                "consistent_count_after": len(diagnostic_posterior),
                "compatibility_fallback_used": step_fallback,
            }
        )
        posterior_sizes.append(len(posterior))

    return SpecificationProbeSelectionResult(
        tuple(selected),
        VersionSpaceEffectModel(
            tool.name,
            tuple(posterior),
            len(diagnostic_posterior),
            fallback_used,
        ),
        tuple(posterior_sizes),
        tuple(scores),
        tuple(diagnostics),
    )
