from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Dict, Iterable, Tuple

import numpy as np


STATE_FIELDS: Tuple[str, ...] = (
    "evidence_present",
    "evidence_verified",
    "supplier_approved",
    "purchase_authorised",
    "report_published",
    "resource_calls",
)


@dataclass(frozen=True)
class PolicyState:
    evidence_present: float = 0.0
    evidence_verified: float = 0.0
    supplier_approved: float = 0.0
    purchase_authorised: float = 0.0
    report_published: float = 0.0
    resource_calls: float = 0.0

    def to_vector(self) -> np.ndarray:
        return np.asarray([float(getattr(self, f)) for f in STATE_FIELDS], dtype=float)

    @classmethod
    def from_vector(cls, values: Iterable[float]) -> "PolicyState":
        vals = list(values)
        if len(vals) != len(STATE_FIELDS):
            raise ValueError(f"Expected {len(STATE_FIELDS)} state values, got {len(vals)}")
        binary = [float(np.clip(round(v), 0, 1)) for v in vals[:-1]]
        resource = float(max(0.0, round(vals[-1])))
        return cls(*binary, resource)

    def evolve(self, **changes: float) -> "PolicyState":
        unknown = set(changes) - set(STATE_FIELDS)
        if unknown:
            raise ValueError(f"Unknown state fields: {sorted(unknown)}")
        return replace(self, **changes)

    def delta(self, other: "PolicyState") -> np.ndarray:
        """Return other - self."""
        return other.to_vector() - self.to_vector()

    def as_dict(self) -> Dict[str, float]:
        return {f: float(getattr(self, f)) for f in STATE_FIELDS}


@dataclass(frozen=True)
class ActionContext:
    agent_role: str
    tool_name: str
    tool_description: str
    arguments: Dict[str, float | str]
