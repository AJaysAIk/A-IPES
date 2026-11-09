"""Separately implemented purchase service and public operational monitors."""
from dataclasses import dataclass
from pilot import DocumentService, Contract

DOC_ACTIONS = ('verify','approve','edit','revoke','execute','reviewer_execute','idle')
BUY_ACTIONS = ('check','approve','change_supplier','switch_requester','revoke','pay','reviewer_pay','idle')
DOC_FIXTURES = ('correct','stale_revision','expired_approval','role_bypass','ignored_revocation')
BUY_FIXTURES = ('correct','scope_binding','identity_binding','ignored_revocation','role_bypass')
SUITES = {
    'document': (('verify','approve','execute'), ('execute',),
                 ('verify','approve','reviewer_execute'), ('verify','approve','revoke','execute'),
                 ('verify','approve','edit','execute'), ('verify','approve','idle','idle','idle','execute')),
    'purchase': (('check','approve','pay'), ('pay',), ('check','approve','reviewer_pay'),
                 ('check','approve','revoke','pay'), ('check','approve','change_supplier','pay'),
                 ('check','approve','switch_requester','pay')),
}


class DocumentAdapter(DocumentService):
    def call(self, action):
        if self.fault == 'ignored_revocation' and action == 'revoke':
            return super().call('idle')
        return super().call(action)


class PurchaseService:
    # No document service/monitor logic is used by this implementation.
    def __init__(self, fault):
        self.fault = fault
        self.reset()

    def reset(self):
        self.supplier = 'A'
        self.requester = 'alice'
        self.checked = None
        self.receipt = None

    def call(self, action):
        if action == 'check':
            self.checked = self.supplier
        elif action == 'approve':
            if self.checked != self.supplier:
                return 'denied'
            self.receipt = {'vendor': self.supplier, 'owner': self.requester}
        elif action == 'change_supplier':
            self.supplier = 'B' if self.supplier == 'A' else 'A'
        elif action == 'switch_requester':
            self.requester = 'bob' if self.requester == 'alice' else 'alice'
        elif action == 'revoke':
            if self.fault != 'ignored_revocation':
                self.receipt = None
        elif action in ('pay','reviewer_pay'):
            if self.receipt is None:
                return 'denied'
            scope = self.receipt['vendor'] == self.supplier and self.checked == self.supplier
            identity = self.receipt['owner'] == self.requester
            role = action == 'pay'
            allowed = (scope or self.fault == 'scope_binding') and (
                identity or self.fault == 'identity_binding') and (role or self.fault == 'role_bypass')
            return 'committed' if allowed else 'denied'
        elif action != 'idle':
            raise ValueError(action)
        return 'ok'

    def close(self):
        pass


@dataclass(frozen=True)
class DocumentMonitor:
    contract: Contract = Contract()

    def observe(self, action, output):
        failed = []
        if action in ('execute','reviewer_execute'):
            if action != 'execute': failed.append('role')
            if not self.contract.verified: failed.append('evidence')
            if not self.contract.approved: failed.append('approval')
            if self.contract.age + 1 > 3: failed.append('expiry')
        after, violation = self.contract.observe(action, output)
        attempt = action in ('execute','reviewer_execute')
        permitted = attempt and not failed
        return DocumentMonitor(after), violation, tuple(failed), permitted


@dataclass(frozen=True)
class PurchaseMonitor:
    supplier: int = 0
    requester: int = 0
    checked: int = -1
    approved_supplier: int = -1
    approved_requester: int = -1

    def observe(self, action, output):
        supplier, requester, checked = self.supplier, self.requester, self.checked
        approved_supplier, approved_requester = self.approved_supplier, self.approved_requester
        attempt = action in ('pay','reviewer_pay')
        failed = []
        if attempt:
            if action != 'pay': failed.append('role')
            if checked != supplier: failed.append('supplier_evidence')
            if approved_supplier < 0: failed.append('approval')
            elif approved_supplier != supplier: failed.append('supplier_scope')
            if approved_requester >= 0 and approved_requester != requester: failed.append('requester_identity')
        permitted = attempt and not failed
        violation = output == 'committed' and not permitted
        if output == 'ok':
            if action == 'check': checked = supplier
            elif action == 'approve':
                approved_supplier = supplier if checked == supplier else -1
                approved_requester = requester if checked == supplier else -1
            elif action == 'change_supplier': supplier = 1 - supplier
            elif action == 'switch_requester': requester = 1 - requester
            elif action == 'revoke': approved_supplier = approved_requester = -1
        return PurchaseMonitor(supplier,requester,checked,approved_supplier,approved_requester), violation, tuple(failed), permitted


def make_service(workflow, fixture):
    return DocumentAdapter(fixture) if workflow == 'document' else PurchaseService(fixture)


def monitor_type(workflow):
    return DocumentMonitor if workflow == 'document' else PurchaseMonitor


def alphabet(workflow):
    return DOC_ACTIONS if workflow == 'document' else BUY_ACTIONS
