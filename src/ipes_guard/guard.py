from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Sequence

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from .domain import ActionContext, PolicyState
from .policy import PolicyViolation, evaluate_transition, infer_effect_class
from .probes import canonical_probe_states
from .signature import EffectModel, effect_signature, fit_effect_model
from .tooling import ToolSpec


@dataclass(frozen=True)
class GuardDecision:
    allow: bool
    predicted_effect_class: str
    violations: tuple[PolicyViolation, ...]
    explanation: str


class IPESGuard:
    """Full multi-probe interventional effect-model guard."""

    def __init__(self, intervention_states: Sequence[PolicyState] | None = None):
        self.intervention_states = list(intervention_states or canonical_probe_states())
        self.models: Dict[str, EffectModel] = {}
        self.signatures: Dict[str, np.ndarray] = {}
        self.effect_classes: Dict[str, str] = {}

    def characterise(self, tools: Iterable[ToolSpec]) -> None:
        for tool in tools:
            model = fit_effect_model(tool, self.intervention_states)
            self.models[tool.name] = model
            self.signatures[tool.name] = effect_signature(model, self.intervention_states)
            self.effect_classes[tool.name] = tool.effect_class

    def decide(self, state: PolicyState, context: ActionContext) -> GuardDecision:
        if context.tool_name not in self.models:
            return GuardDecision(
                allow=False,
                predicted_effect_class="unknown",
                violations=(
                    PolicyViolation(
                        "UNCHARACTERISED_TOOL",
                        "The tool has no intervention-derived effect model.",
                    ),
                ),
                explanation="Blocked because the tool was not characterised before admission.",
            )
        model = self.models[context.tool_name]
        after = model.predict(state)
        effect = infer_effect_class(state, after)
        violations = tuple(evaluate_transition(state, after, context, effect))
        return GuardDecision(
            allow=not violations,
            predicted_effect_class=effect,
            violations=violations,
            explanation=(
                f"Predicted effect={effect}; "
                + ("no policy violation" if not violations else "; ".join(v.message for v in violations))
            ),
        )


class SingleProbeEffectGuard(IPESGuard):
    """Ablation: characterise each tool in only one default state."""

    def __init__(self):
        super().__init__([PolicyState()])


class ManualNameGuard:
    """Exact-name baseline. Unknown names are treated as no-effect."""

    NAME_TO_EFFECT = {
        "retrieve_supplier_evidence": "retrieve_evidence",
        "verify_supplier_evidence": "verify_evidence",
        "approve_supplier": "approve_supplier",
        "authorise_purchase": "authorise_purchase",
        "publish_emissions_report": "publish_report",
        "query_compliance_service": "consume_resource",
        "preview_supplier_approval": "no_effect",
        "review_supplier": "no_effect",
    }

    def decide(self, state: PolicyState, context: ActionContext) -> GuardDecision:
        effect = self.NAME_TO_EFFECT.get(context.tool_name, "no_effect")
        after = apply_symbolic_effect(state, effect, context.arguments)
        violations = tuple(evaluate_transition(state, after, context, effect))
        return GuardDecision(
            allow=not violations,
            predicted_effect_class=effect,
            violations=violations,
            explanation=f"Manual exact-name mapping predicted effect={effect}.",
        )


class TextSemanticGuard:
    """Text-only interface classifier baseline."""

    def __init__(self):
        self.pipeline = Pipeline(
            [
                ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
                (
                    "classifier",
                    LogisticRegression(
                        max_iter=3000,
                        class_weight="balanced",
                        random_state=0,
                    ),
                ),
            ]
        )
        self._fitted = False

    def fit(self, tools: Sequence[ToolSpec]) -> None:
        self.pipeline.fit([t.interface_text for t in tools], [t.effect_class for t in tools])
        self._fitted = True

    def decide(self, state: PolicyState, context: ActionContext) -> GuardDecision:
        if not self._fitted:
            raise RuntimeError("TextSemanticGuard.fit must be called before decide.")
        text = (
            f"name={context.tool_name}; description={context.tool_description}; "
            f"arguments={', '.join(context.arguments.keys())}"
        )
        effect = str(self.pipeline.predict([text])[0])
        after = apply_symbolic_effect(state, effect, context.arguments)
        violations = tuple(evaluate_transition(state, after, context, effect))
        return GuardDecision(
            allow=not violations,
            predicted_effect_class=effect,
            violations=violations,
            explanation=f"Text-semantic classifier predicted effect={effect}.",
        )


def apply_symbolic_effect(
    state: PolicyState,
    effect: str,
    arguments: Mapping[str, float | str],
) -> PolicyState:
    if effect == "retrieve_evidence":
        return state.evolve(evidence_present=1)
    if effect == "verify_evidence":
        return state.evolve(evidence_verified=1 if state.evidence_present else 0)
    if effect == "approve_supplier":
        return state.evolve(supplier_approved=1)
    if effect == "authorise_purchase":
        return state.evolve(purchase_authorised=1)
    if effect == "publish_report":
        return state.evolve(report_published=1)
    if effect == "consume_resource":
        amount = float(arguments.get("calls", arguments.get("units", 1.0)))
        return state.evolve(resource_calls=state.resource_calls + amount)
    return state
