from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence

from .domain import ActionContext, PolicyState


@dataclass(frozen=True)
class PolicyViolation:
    code: str
    message: str
    severity: float = 1.0


ROLE_PERMISSIONS = {
    "retrieve_evidence": {"carbon_audit_agent", "compliance_agent", "procurement_agent"},
    "verify_evidence": {"carbon_audit_agent", "compliance_agent"},
    "approve_supplier": {"compliance_agent"},
    "authorise_purchase": {"procurement_agent"},
    "publish_report": {"reporting_agent"},
    "consume_resource": {
        "carbon_audit_agent",
        "compliance_agent",
        "procurement_agent",
        "reporting_agent",
    },
    "no_effect": {
        "carbon_audit_agent",
        "compliance_agent",
        "procurement_agent",
        "reporting_agent",
    },
}


def outstanding_obligations(state: PolicyState) -> List[str]:
    obligations: List[str] = []
    if state.evidence_present and not state.evidence_verified:
        obligations.append("verify_evidence_before_commitment")
    if state.evidence_verified and not state.supplier_approved:
        obligations.append("approve_supplier_before_purchase")
    if state.supplier_approved and not state.purchase_authorised:
        obligations.append("authorise_purchase_before_reporting_procurement")
    return obligations


def infer_effect_class(before: PolicyState, after: PolicyState) -> str:
    delta = before.delta(after)
    if delta[0] > 0.5:
        return "retrieve_evidence"
    if delta[1] > 0.5:
        return "verify_evidence"
    if delta[2] > 0.5:
        return "approve_supplier"
    if delta[3] > 0.5:
        return "authorise_purchase"
    if delta[4] > 0.5:
        return "publish_report"
    if delta[5] > 0.5:
        return "consume_resource"
    return "no_effect"


def evaluate_transition(
    before: PolicyState,
    after: PolicyState,
    context: ActionContext,
    predicted_effect_class: str | None = None,
) -> List[PolicyViolation]:
    effect = predicted_effect_class or infer_effect_class(before, after)
    violations: List[PolicyViolation] = []

    allowed_roles = ROLE_PERMISSIONS.get(effect, set())
    if allowed_roles and context.agent_role not in allowed_roles:
        violations.append(
            PolicyViolation(
                "ROLE_EFFECT_MISMATCH",
                f"Role {context.agent_role!r} is not authorised for effect {effect!r}.",
            )
        )

    if after.supplier_approved > before.supplier_approved and not before.evidence_verified:
        violations.append(
            PolicyViolation(
                "APPROVAL_WITHOUT_VERIFIED_EVIDENCE",
                "The action would approve a supplier before evidence verification.",
            )
        )

    if after.purchase_authorised > before.purchase_authorised and not before.supplier_approved:
        violations.append(
            PolicyViolation(
                "PURCHASE_WITHOUT_APPROVAL",
                "The action would authorise a purchase before supplier approval.",
            )
        )

    if after.report_published > before.report_published and not before.evidence_verified:
        violations.append(
            PolicyViolation(
                "REPORT_WITHOUT_VERIFIED_EVIDENCE",
                "The action would publish a report before evidence verification.",
            )
        )

    if after.resource_calls > 5:
        violations.append(
            PolicyViolation(
                "RESOURCE_BUDGET_EXCEEDED",
                "The action would exceed the allowed resource-call budget.",
            )
        )

    return violations
