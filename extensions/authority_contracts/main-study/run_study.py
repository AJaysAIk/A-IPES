"""Frozen synthetic comparison; all actual service calls share one audited budget."""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import platform
import random
import sys
import time
from collections import Counter, deque
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from aalpy.base import Oracle, SUL
from aalpy.learning_algs import run_Lstar
from aalpy.oracles import BBCEqOracle, RandomWMethodEqOracle
from pilot import BudgetExhausted
from services import DOC_FIXTURES, BUY_FIXTURES, SUITES, alphabet, make_service, monitor_type

BUDGETS = (250, 1000, 2000)
STRATEGIES = ('Lstar_BBC_then_random', 'Lstar_W_then_random', 'contract_suite_then_random', 'random')


class ActualSUL(SUL):
    def __init__(self, workflow, fixture, cap):
        super().__init__()
        self.service = make_service(workflow, fixture)
        self.monitor_factory = monitor_type(workflow)
        self.cap = cap
        self.calls = self.resets = 0
        self.phase = 'learning'
        self.audit = []
        self.monitor, self.trace = self.monitor_factory(), []

    def pre(self):
        self.service.reset()
        self.monitor, self.trace = self.monitor_factory(), []
        self.resets += 1

    def post(self):
        pass

    def step(self, action):
        if self.calls >= self.cap:
            raise BudgetExhausted()
        output = self.service.call(action)
        self.calls += 1
        self.trace.append(action)
        self.monitor, bad, clauses, permitted = self.monitor.observe(action, output)
        self.audit.append({'call': self.calls, 'reset': self.resets, 'phase': self.phase,
                           'trace': tuple(self.trace), 'action': action, 'output': output,
                           'violation': bad, 'failed_clauses': clauses,
                           'permitted_attempt': permitted,
                           'permitted_commit': permitted and output == 'committed'})
        return output


class TrackedW(RandomWMethodEqOracle):
    def __init__(self, actions, sul):
        super().__init__(actions, sul, walks_per_state=10, walk_len=6)
        self.actual = sul
        self.disagreements = 0

    def find_cex(self, hypothesis):
        previous, self.actual.phase = self.actual.phase, 'equivalence'
        try:
            result = super().find_cex(hypothesis)
            self.disagreements += result is not None
            return result
        finally:
            self.actual.phase = previous


class ProductOracle(Oracle):
    def __init__(self, actions, sul):
        super().__init__(actions, sul)
        self.factory = sul.monitor_factory
        self.checks = self.edges = self.predicted = 0

    def find_cex(self, hypothesis):
        self.checks += 1
        initial = self.factory()
        queue = deque([(hypothesis.initial_state, initial, ())])
        visited = {(hypothesis.initial_state.state_id, initial)}
        while queue:
            state, monitor, trace = queue.popleft()
            if len(trace) >= 6:
                continue
            for action in self.alphabet:
                output = state.output_fun[action]
                after, bad, _, _ = monitor.observe(action, output)
                self.edges += 1
                if bad:
                    self.predicted += 1
                    return trace + (action,)
                target = state.transitions[action]
                key = target.state_id, after
                if key not in visited:
                    visited.add(key)
                    queue.append((target, after, trace + (action,)))
        return None


class TrackedBBC(BBCEqOracle):
    def __init__(self, eq, prop, actual):
        super().__init__(eq, {'authority': prop})
        self.actual = actual
        self.refinement_counterexamples = 0

    def find_cex(self, hypothesis):
        previous, self.actual.phase = self.actual.phase, 'property_validation'
        try:
            result = super().find_cex(hypothesis)
            self.refinement_counterexamples += result is not None
            return result
        finally:
            self.actual.phase = previous


def random_suffix(sul, actions, seed):
    rng = random.Random(seed)
    sul.phase = 'random_fill'
    while sul.calls < sul.cap:
        sul.pre()
        for _ in range(min(6, sul.cap - sul.calls)):
            sul.step(rng.choice(actions))


def run_case(workflow, fixture, strategy, seed, cap=2000, budgets=BUDGETS):
    random.seed(seed)
    actions = list(alphabet(workflow))
    sul = ActualSUL(workflow, fixture, cap)
    started = time.perf_counter()
    learned_states = None
    eq = prop = outer = None
    termination = 'no_learner'
    try:
        if strategy.startswith('Lstar_'):
            eq = TrackedW(actions, sul)
            prop = ProductOracle(actions, sul) if strategy == 'Lstar_BBC_then_random' else None
            outer = TrackedBBC(eq, prop, sul) if prop else eq
            try:
                learned = run_Lstar(actions, sul, outer, 'mealy', print_level=0)
                learned_states = len(learned.states)
                termination = 'approximate_oracle_returned'
            except BudgetExhausted:
                termination = 'budget_exhausted_during_learning'
        elif strategy == 'contract_suite_then_random':
            sul.phase = 'contract_suite'
            for trace in SUITES[workflow]:
                sul.pre()
                for action in trace:
                    sul.step(action)
        elif strategy != 'random':
            raise ValueError(strategy)
        random_suffix(sul, actions, seed)
        assert sul.calls == cap
        case = {'workflow': workflow, 'fixture': fixture, 'strategy': strategy, 'seed': seed}
        rows = []
        for budget in budgets:
            prefix = sul.audit[:budget]
            assert len(prefix) == budget
            violations = [r for r in prefix if r['violation']]
            attempts = sum(r['permitted_attempt'] for r in prefix)
            commits = sum(r['permitted_commit'] for r in prefix)
            phases = Counter(r['phase'] for r in prefix)
            rows.append({**case, 'budget': budget, 'executed_calls': len(prefix),
                         'resets_through_last_action': prefix[-1]['reset'],
                         'violation_detected': bool(violations),
                         'first_violation_call': violations[0]['call'] if violations else None,
                         'permitted_attempts': attempts, 'permitted_commits': commits,
                         'permitted_acceptance': commits / attempts if attempts else None,
                         'challenged_clauses': '|'.join(sorted({c for r in prefix for c in r['failed_clauses']})),
                         'violated_clauses': '|'.join(sorted({c for r in violations for c in r['failed_clauses']})),
                         **{f'{p}_calls': phases[p] for p in ('learning','equivalence','property_validation','contract_suite','random_fill')}})
        telemetry = {**case, 'executed_calls': sul.calls, 'requested_resets': sul.resets,
                     'termination': termination, 'learned_states': learned_states,
                     'cache_hits_reported': getattr(eq.sul, 'num_cached_queries', None) if eq else None,
                     'equivalence_disagreements': eq.disagreements if eq else None,
                     'bbc_refinement_counterexamples': outer.refinement_counterexamples if isinstance(outer, TrackedBBC) else None,
                     'confirmed_bbc_properties': sorted(outer.violated_properties) if isinstance(outer, TrackedBBC) else None,
                     'model_checks': prop.checks if prop else None,
                     'model_edges': prop.edges if prop else None,
                     'predicted_counterexamples': prop.predicted if prop else None}
        wall = {**case, 'wall_seconds': time.perf_counter() - started}
        return rows, [{**case, **r} for r in sul.audit], telemetry, wall
    finally:
        sul.service.close()


def write_csv(path, rows):
    with path.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit('Existing results are preserved; select a new directory.')
    expected = (ROOT / 'protocol.sha256').read_text().split()[0]
    assert hashlib.sha256((ROOT / 'PROTOCOL.md').read_bytes()).hexdigest() == expected
    args.output.mkdir(parents=True)
    status = args.output / 'status.json'
    status.write_text(json.dumps({'status': 'running'}) + '\n')
    rows, runs, times = [], [], []
    try:
        with (args.output / 'actions.jsonl.gz').open('wb') as raw:
            with gzip.GzipFile(fileobj=raw, filename='', mode='wb', mtime=0) as handle:
                for workflow, fixtures in (('document', DOC_FIXTURES), ('purchase', BUY_FIXTURES)):
                    for fixture in fixtures:
                        for seed in range(10):
                            for strategy in STRATEGIES:
                                prefix, actions, telemetry, wall = run_case(workflow, fixture, strategy, seed)
                                rows.extend(prefix)
                                runs.append(telemetry)
                                times.append(wall)
                                for action in actions:
                                    handle.write((json.dumps(action, sort_keys=True) + '\n').encode())
                        print(f'completed {workflow}/{fixture}', flush=True)
        write_csv(args.output / 'prefixes.csv', rows)
        (args.output / 'runs.json').write_text(json.dumps(runs, indent=2, sort_keys=True) + '\n')
        (args.output / 'wall_times.json').write_text(json.dumps(times, indent=2, sort_keys=True) + '\n')
        sources = [ROOT / 'PROTOCOL.md', ROOT / 'services.py', Path(__file__), ROOT.parent / 'pilot.py']
        (args.output / 'provenance.json').write_text(json.dumps({
            'scope': 'prospectively reserved synthetic evaluation, not independently sampled systems',
            'protocol_freeze': 'local SHA256 before selector outcomes; not external preregistration',
            'protocol_sha256': expected, 'aalpy': version('aalpy'), 'python': platform.python_version(),
            'source_sha256': {str(p.relative_to(ROOT.parent)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
            'runs': len(runs), 'prefix_rows': len(rows), 'executed_calls': sum(r['executed_calls'] for r in runs),
        }, indent=2, sort_keys=True) + '\n')
        status.write_text(json.dumps({'status': 'complete', 'runs': len(runs)}) + '\n')
    except Exception as exc:
        status.write_text(json.dumps({'status': 'failed', 'completed_runs': len(runs), 'error': repr(exc)}) + '\n')
        raise


if __name__ == '__main__':
    main()
