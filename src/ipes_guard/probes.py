from __future__ import annotations

from typing import List

from .domain import PolicyState


def canonical_probe_states() -> List[PolicyState]:
    """Probe states deliberately cover prerequisite boundaries."""
    return [
        PolicyState(),
        PolicyState(evidence_present=1),
        PolicyState(evidence_present=1, evidence_verified=1),
        PolicyState(evidence_present=1, evidence_verified=1, supplier_approved=1),
        PolicyState(
            evidence_present=1,
            evidence_verified=1,
            supplier_approved=1,
            purchase_authorised=1,
        ),
        PolicyState(resource_calls=5),
    ]
