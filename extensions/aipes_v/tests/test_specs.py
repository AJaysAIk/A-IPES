from aipes_v.specs import default_specifications, violated_names, violation_signature
from ipes_guard.domain import PolicyState


def test_default_specifications_cover_four_explicit_properties():
    specs = default_specifications()
    assert len(specs) == 4
    assert len({spec.name for spec in specs}) == 4


def test_unsafe_approval_is_detected():
    before = PolicyState(evidence_verified=0)
    after = before.evolve(supplier_approved=1)
    assert "verified_before_supplier_approval" in violated_names(before, after)


def test_safe_approval_does_not_violate_prerequisite():
    before = PolicyState(evidence_verified=1)
    after = before.evolve(supplier_approved=1)
    assert not any(violation_signature(before, after))


def test_resource_limit_is_transition_monitored():
    before = PolicyState(resource_calls=5)
    after = before.evolve(resource_calls=6)
    assert "resource_call_budget" in violated_names(before, after)
