"""Development feasibility only: standard learning/BBC against a SQLite tool."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import sqlite3
from collections import deque
from dataclasses import dataclass
from importlib.metadata import version
from pathlib import Path

from aalpy.base import Oracle, SUL
from aalpy.learning_algs import run_Lstar
from aalpy.oracles import BBCEqOracle, RandomWMethodEqOracle

ACTIONS = ('verify', 'approve', 'edit', 'revoke', 'execute', 'reviewer_execute', 'idle')
FIXTURES = ('correct', 'stale_revision', 'expired_approval', 'role_bypass')


class DocumentService:
    def __init__(self, fault):
        self.fault = fault
        self.db = sqlite3.connect(':memory:')
        self.db.execute('CREATE TABLE document(revision INTEGER, evidence INTEGER, approval INTEGER, granted INTEGER, clock INTEGER)')
        self.reset()

    def reset(self):
        self.db.execute('DELETE FROM document')
        self.db.execute('INSERT INTO document VALUES(0, -1, -1, -1, 0)')

    def call(self, action):
        revision, evidence, approval, granted, clock = self.db.execute('SELECT * FROM document').fetchone()
        clock += 1
        output = 'ok'
        if action == 'verify':
            evidence = revision
        elif action == 'approve':
            if evidence == revision:
                approval, granted = revision, clock
            else:
                output = 'denied'
        elif action == 'edit':
            revision += 1
        elif action == 'revoke':
            approval, granted = -1, -1
        elif action in ('execute', 'reviewer_execute'):
            fresh = approval == revision and evidence == revision
            if self.fault == 'stale_revision':
                fresh = approval >= 0
            timely = clock - granted <= 3 or self.fault == 'expired_approval'
            role_ok = action == 'execute' or self.fault == 'role_bypass'
            output = 'committed' if granted >= 0 and fresh and timely and role_ok else 'denied'
        elif action != 'idle':
            raise ValueError(action)
        self.db.execute('UPDATE document SET revision=?, evidence=?, approval=?, granted=?, clock=?',
                        (revision, evidence, approval, granted, clock))
        return output

    def close(self):
        self.db.close()


@dataclass(frozen=True)
class Contract:
    verified: bool = False
    approved: bool = False
    age: int = 4

    def observe(self, action, output):
        age = min(4, self.age + 1)
        verified, approved = self.verified, self.approved
        violation = output == 'committed' and not (
            action == 'execute' and verified and approved and age <= 3
        )
        if action == 'verify' and output == 'ok':
            verified = True
        elif action == 'approve' and output == 'ok':
            # Authorization requires previously observed verified evidence.
            approved, age = verified, 0
        elif action == 'edit' and output == 'ok':
            verified, approved = False, False
        elif action == 'revoke' and output == 'ok':
            approved = False
        return Contract(verified, approved, age), violation


class BudgetExhausted(Exception):
    pass


class AuditedService(SUL):
    def __init__(self, fault, budget):
        super().__init__()
        self.service = DocumentService(fault)
        self.budget = budget
        self.calls = self.resets = 0
        self.audit = []
        self.first_violation = None
        self.monitor = Contract()
        self.trace = []

    def pre(self):
        self.service.reset()
        self.monitor, self.trace = Contract(), []
        self.resets += 1

    def post(self):
        pass

    def step(self, action):
        if self.calls >= self.budget:
            raise BudgetExhausted()
        output = self.service.call(action)
        self.calls += 1
        self.trace.append(action)
        self.monitor, violation = self.monitor.observe(action, output)
        if violation and self.first_violation is None:
            self.first_violation = self.calls
        self.audit.append({'call': self.calls, 'reset': self.resets,
                           'trace': tuple(self.trace), 'action': action,
                           'output': output, 'violation': violation})
        return output


class BoundedContractOracle(Oracle):
    def __init__(self, alphabet, sul, depth=6):
        super().__init__(alphabet, sul)
        self.depth = depth
        self.hypotheses_checked = 0
        self.predicted_counterexamples = 0
        self.model_edges_checked = 0

    def find_cex(self, hypothesis):
        self.hypotheses_checked += 1
        queue = deque([(hypothesis.initial_state, Contract(), ())])
        visited = {(hypothesis.initial_state.state_id, Contract())}
        while queue:
            state, monitor, trace = queue.popleft()
            if len(trace) >= self.depth:
                continue
            for action in self.alphabet:
                output = state.output_fun[action]
                after, bad = monitor.observe(action, output)
                self.model_edges_checked += 1
                if bad:
                    self.predicted_counterexamples += 1
                    return trace + (action,)
                target = state.transitions[action]
                key = target.state_id, after
                if key not in visited:
                    visited.add(key)
                    queue.append((target, after, trace + (action,)))
        return None


def fill_random(sul, rng):
    while sul.calls < sul.budget:
        sul.pre()
        for _ in range(min(6, sul.budget - sul.calls)):
            sul.step(rng.choice(ACTIONS))
        sul.post()


def run_case(fault, strategy, seed, budget=1000):
    random.seed(seed)
    sul = AuditedService(fault, budget)
    learned_states = None
    termination = 'random_budget'
    prop = None
    if strategy == 'Lstar_BBC_then_random':
        prop = BoundedContractOracle(list(ACTIONS), sul)
        eq = RandomWMethodEqOracle(list(ACTIONS), sul, walks_per_state=10, walk_len=6)
        bbc = BBCEqOracle(eq, {'authority': prop})
        try:
            model = run_Lstar(list(ACTIONS), sul, bbc, 'mealy', print_level=0)
            learned_states = len(model.states)
            termination = 'approximate_oracle_returned_then_random'
        except BudgetExhausted:
            termination = 'budget_exhausted_during_learning'
    elif strategy != 'random':
        raise ValueError(strategy)
    fill_random(sul, random.Random(seed))
    summary = {'fixture': fault, 'strategy': strategy, 'seed': seed, 'budget': budget,
               'executed_calls': sul.calls, 'resets': sul.resets,
               'violation_detected': sul.first_violation is not None,
               'first_violation_call': sul.first_violation, 'termination': termination,
               'learned_states': learned_states,
               'hypotheses_checked': 0 if prop is None else prop.hypotheses_checked,
               'predicted_counterexamples': 0 if prop is None else prop.predicted_counterexamples,
               'model_edges_checked': 0 if prop is None else prop.model_edges_checked}
    audits = [{**row, 'fixture': fault, 'strategy': strategy, 'seed': seed} for row in sul.audit]
    sul.service.close()
    return summary, audits


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit('Use a new output directory; existing results are preserved.')
    root = Path(__file__).parent
    expected = (root / 'protocol.sha256').read_text().split()[0]
    assert hashlib.sha256((root / 'FEASIBILITY_PROTOCOL.md').read_bytes()).hexdigest() == expected
    rows, audits = [], []
    for seed in (0, 1, 2):
        for fault in FIXTURES:
            for strategy in ('Lstar_BBC_then_random', 'random'):
                row, trace = run_case(fault, strategy, seed)
                rows.append(row)
                audits.extend(trace)
    args.output.mkdir(parents=True)
    with (args.output / 'summary.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with (args.output / 'actions.jsonl').open('w') as handle:
        for row in audits:
            handle.write(json.dumps(row, sort_keys=True) + '\n')
    (args.output / 'provenance.json').write_text(json.dumps({
        'status': 'development feasibility only; no held-out evidence',
        'aalpy_version': version('aalpy'), 'protocol_sha256': expected,
        'pilot_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'cases': len(rows), 'executed_calls': len(audits),
    }, indent=2) + '\n')
    print(f'{len(rows)} feasibility cases; {len(audits)} audited calls. No generalization claim.')


if __name__ == '__main__':
    main()
