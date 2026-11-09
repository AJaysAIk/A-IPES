import unittest
from itertools import product

from aalpy.automata import MealyMachine, MealyState
from aalpy.oracles import BBCEqOracle, RandomWMethodEqOracle

from pilot import ACTIONS, AuditedService, BoundedContractOracle, Contract, DocumentService, run_case


class FeasibilityTests(unittest.TestCase):
    def test_separate_fault_witnesses(self):
        witnesses = {
            'stale_revision': ('verify', 'approve', 'edit', 'execute'),
            'expired_approval': ('verify', 'approve', 'idle', 'idle', 'idle', 'execute'),
            'role_bypass': ('verify', 'approve', 'reviewer_execute'),
        }
        for fault, trace in witnesses.items():
            sul = AuditedService(fault, 100)
            sul.pre()
            for action in trace:
                sul.step(action)
            self.assertTrue(sul.audit[-1]['violation'], fault)
            control = AuditedService('correct', 100)
            control.pre()
            for action in trace:
                control.step(action)
            self.assertIsNone(control.first_violation)
            sul.service.close()
            control.service.close()

    def test_monitor_independent_fixtures(self):
        monitor = Contract()
        for action in ('verify', 'approve'):
            monitor, bad = monitor.observe(action, 'ok')
            self.assertFalse(bad)
        _, bad = monitor.observe('execute', 'committed')
        self.assertFalse(bad)
        _, bad = monitor.observe('reviewer_execute', 'committed')
        self.assertTrue(bad)
        for action in ('idle', 'idle', 'idle'):
            monitor, _ = monitor.observe(action, 'ok')
        _, bad = monitor.observe('execute', 'committed')
        self.assertTrue(bad)

    def test_correct_service_all_short_traces(self):
        service = DocumentService('correct')
        for trace in product(ACTIONS, repeat=4):
            service.reset()
            monitor = Contract()
            for action in trace:
                monitor, bad = monitor.observe(action, service.call(action))
                self.assertFalse(bad, trace)
        service.close()

    def test_standard_bbc_validates_a_spurious_model_counterexample(self):
        sul = AuditedService('correct', 100)
        state = MealyState('bad-model')
        for action in ACTIONS:
            state.transitions[action] = state
            state.output_fun[action] = 'committed'
        hypothesis = MealyMachine(state, [state])
        prop = BoundedContractOracle(list(ACTIONS), sul)
        self.assertEqual(prop.find_cex(hypothesis), ('verify',))
        self.assertEqual(sul.calls, 0)
        eq = RandomWMethodEqOracle(list(ACTIONS), sul, walks_per_state=1, walk_len=1)
        bbc = BBCEqOracle(eq, {'authority': prop})
        self.assertEqual(bbc.find_cex(hypothesis), ('verify',))
        self.assertEqual(sul.calls, 1)
        self.assertFalse(bbc.violated_properties)
        self.assertIsNone(sul.first_violation)
        sul.service.close()

    def test_exact_budget_and_reproducible_audits(self):
        for strategy in ('Lstar_BBC_then_random', 'random'):
            one = run_case('expired_approval', strategy, 0, budget=37)
            self.assertEqual(one, run_case('expired_approval', strategy, 0, budget=37))
            summary, audits = one
            self.assertEqual(summary['executed_calls'], 37)
            self.assertEqual(len(audits), 37)
            self.assertEqual([r['call'] for r in audits], list(range(1, 38)))
            self.assertEqual(audits[-1]['reset'], summary['resets'])


if __name__ == '__main__':
    unittest.main()
