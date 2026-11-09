import unittest
from itertools import product

from aalpy.automata import MealyMachine, MealyState
from run_study import ActualSUL, ProductOracle, TrackedBBC, TrackedW, STRATEGIES, run_case
from services import BUY_ACTIONS, PurchaseService, PurchaseMonitor, DocumentMonitor, DocumentAdapter


class StudyChecks(unittest.TestCase):
    def replay(self, service, factory, trace):
        monitor, bad = factory(), []
        for action in trace:
            monitor, violation, _, _ = monitor.observe(action, service.call(action))
            bad.append(violation)
        return bad

    def test_purchase_fault_witnesses(self):
        traces = {
            'scope_binding': ('check','approve','change_supplier','pay'),
            'identity_binding': ('check','approve','switch_requester','pay'),
            'ignored_revocation': ('check','approve','revoke','pay'),
            'role_bypass': ('check','approve','reviewer_pay'),
        }
        for fault, trace in traces.items():
            self.assertTrue(self.replay(PurchaseService(fault), PurchaseMonitor, trace)[-1])
            self.assertFalse(any(self.replay(PurchaseService('correct'), PurchaseMonitor, trace)))

    def test_correct_purchase_exhaustive_short_traces(self):
        service = PurchaseService('correct')
        for trace in product(BUY_ACTIONS, repeat=4):
            service.reset()
            self.assertFalse(any(self.replay(service, PurchaseMonitor, trace)), trace)

    def test_returning_to_approved_scope_and_identity_is_permitted(self):
        for middle in (('change_supplier','change_supplier'), ('switch_requester','switch_requester')):
            service = PurchaseService('correct')
            trace = ('check','approve') + middle + ('pay',)
            monitor = PurchaseMonitor()
            for action in trace:
                output = service.call(action)
                monitor, bad, _, permitted = monitor.observe(action, output)
                self.assertFalse(bad)
            self.assertTrue(permitted)
            self.assertEqual(output, 'committed')

    def test_new_document_revocation_fixture(self):
        trace = ('verify','approve','revoke','execute')
        for fault in ('correct','ignored_revocation'):
            service = DocumentAdapter(fault)
            bad = self.replay(service, DocumentMonitor, trace)
            self.assertEqual(bad[-1], fault == 'ignored_revocation')
            service.close()

    def test_public_monitor_does_not_require_hidden_state(self):
        monitor = PurchaseMonitor()
        for action in ('check','approve','switch_requester'):
            monitor, _, _, _ = monitor.observe(action, 'ok')
        _, bad, failed, permitted = monitor.observe('pay','committed')
        self.assertTrue(bad)
        self.assertFalse(permitted)
        self.assertEqual(failed, ('requester_identity',))
        _, bad, _, _ = monitor.observe('pay','denied')
        self.assertFalse(bad)

    def test_spurious_bbc_validation_has_separate_phase(self):
        sul = ActualSUL('purchase','correct',100)
        state = MealyState('bad-model')
        for action in BUY_ACTIONS:
            state.transitions[action] = state
            state.output_fun[action] = 'committed'
        prop = ProductOracle(list(BUY_ACTIONS), sul)
        oracle = TrackedBBC(TrackedW(list(BUY_ACTIONS), sul), prop, sul)
        self.assertEqual(oracle.find_cex(MealyMachine(state,[state])), ('check',))
        self.assertEqual(sul.audit[0]['phase'], 'property_validation')
        self.assertFalse(sul.audit[0]['violation'])
        self.assertFalse(oracle.violated_properties)
        self.assertEqual(sul.phase, 'learning')
        sul.service.close()

    def test_budget_prefixes_and_reproducibility(self):
        for strategy in STRATEGIES:
            large = run_case('purchase','scope_binding',strategy,0,cap=100,budgets=(50,100))
            again = run_case('purchase','scope_binding',strategy,0,cap=100,budgets=(50,100))
            small = run_case('purchase','scope_binding',strategy,0,cap=50,budgets=(50,))
            self.assertEqual(large[:3], again[:3])
            self.assertEqual(large[1][:50], small[1])
            self.assertEqual(large[0][0], small[0][0])
            self.assertEqual(len(large[1]),100)
            self.assertEqual([r['call'] for r in large[1]],list(range(1,101)))
            for row in large[0]:
                phases = sum(row[f'{p}_calls'] for p in ('learning','equivalence','property_validation','contract_suite','random_fill'))
                self.assertEqual(phases,row['budget'])
                self.assertLessEqual(row['permitted_commits'],row['permitted_attempts'])


if __name__ == '__main__':
    unittest.main()
