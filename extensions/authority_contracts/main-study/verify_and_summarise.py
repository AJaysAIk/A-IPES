"""Replay saved evidence without invoking any test-selection strategy."""
import argparse
import csv
import gzip
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from services import make_service, monitor_type

parser = argparse.ArgumentParser()
parser.add_argument('results', type=Path)
args = parser.parse_args()
base = args.results
with (base / 'prefixes.csv').open() as handle:
    rows = list(csv.DictReader(handle))
with (base / 'runs.json').open() as handle:
    runs = json.load(handle)

fields = ('workflow','fixture','strategy','seed')
def key(row):
    return tuple(str(row[f]) for f in fields)
lookup = {(key(row),int(row['budget'])):row for row in rows}
assert len(lookup) == len(rows) == 1200
telemetry = {key(row):row for row in runs}
assert len(telemetry) == len(runs) == 400
phases = ('learning','equivalence','property_validation','contract_suite','random_fill')
finished = set()
active = None
service = None
seen_prefixes = set()
actual_calls = 0
with gzip.open(base / 'actions.jsonl.gz', 'rt') as handle:
    for line in handle:
        record = json.loads(line)
        case = key(record)
        if case != active:
            if active is not None:
                assert count == 2000
                assert active not in finished
                finished.add(active)
                service.close()
            assert case not in finished
            active = case
            service = make_service(record['workflow'], record['fixture'])
            factory = monitor_type(record['workflow'])
            count = last_reset = 0
            first = None
            attempts = commits = 0
            challenge, violated, phase_count = set(), set(), Counter()
        if record['reset'] != last_reset:
            assert record['reset'] > last_reset
            last_reset = record['reset']
            service.reset()
            monitor = factory()
            trace = []
        count += 1
        actual_calls += 1
        assert record['call'] == count
        output = service.call(record['action'])
        assert output == record['output']
        trace.append(record['action'])
        assert trace == record['trace']
        monitor, bad, clauses, permitted = monitor.observe(record['action'], output)
        assert bad == record['violation']
        assert list(clauses) == record['failed_clauses']
        assert permitted == record['permitted_attempt']
        assert (permitted and output == 'committed') == record['permitted_commit']
        assert record['phase'] in phases
        phase_count[record['phase']] += 1
        attempts += permitted
        commits += permitted and output == 'committed'
        challenge.update(clauses)
        if bad:
            if first is None: first = count
            violated.update(clauses)
        if count in (250,1000,2000):
            row = lookup[case,count]
            seen_prefixes.add((case,count))
            assert int(row['executed_calls']) == count
            assert row['violation_detected'] == str(first is not None)
            assert row['first_violation_call'] == (str(first) if first is not None else '')
            assert int(row['resets_through_last_action']) == last_reset
            assert int(row['permitted_attempts']) == attempts
            assert int(row['permitted_commits']) == commits
            assert row['permitted_acceptance'] == (str(commits/attempts) if attempts else '')
            assert row['challenged_clauses'] == '|'.join(sorted(challenge))
            assert row['violated_clauses'] == '|'.join(sorted(violated))
            assert all(int(row[f'{p}_calls']) == phase_count[p] for p in phases)
            assert sum(phase_count.values()) == count
            if record['fixture'] == 'correct': assert first is None
assert count == 2000
service.close()
finished.add(active)
assert finished == set(telemetry)
assert seen_prefixes == set(lookup)
assert actual_calls == 800000
for r in runs:
    assert r['executed_calls'] == 2000
provenance = json.loads((base / 'provenance.json').read_text())
for source, expected in provenance['source_sha256'].items():
    assert hashlib.sha256((ROOT.parent / source).read_bytes()).hexdigest() == expected

groups = defaultdict(list)
for row in rows:
    groups[row['workflow'],row['fixture'],row['strategy'],int(row['budget'])].append(row)
summary = []
for (workflow,fixture,strategy,budget), group in sorted(groups.items()):
    assert len(group) == 10
    summary.append({'workflow':workflow,'fixture':fixture,'strategy':strategy,'budget':budget,
                    'detections':sum(r['violation_detected']=='True' for r in group),
                    'cases':len(group),'permitted_attempts':sum(int(r['permitted_attempts']) for r in group),
                    'permitted_commits':sum(int(r['permitted_commits']) for r in group)})
with (base / 'summary.csv').open('w',newline='') as handle:
    writer = csv.DictWriter(handle,fieldnames=list(summary[0]))
    writer.writeheader();writer.writerows(summary)
report = {'verification':'passed','action_records_replayed':actual_calls,'runs':len(finished),
          'prefixes_checked':len(seen_prefixes),'source_hashes_checked':len(provenance['source_sha256']),
          'scope':'separate-pass replay using service implementation and public monitor; not an independent judge implementation'}
(base / 'verification.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps(report))
for workflow in ('document','purchase'):
    print(workflow,'unsafe detections / 40 at budgets 250, 1000, 2000')
    for strategy in sorted({r['strategy'] for r in rows}):
        print(strategy,[(b,sum(int(r['detections']) for r in summary if r['workflow']==workflow and r['fixture']!='correct' and r['strategy']==strategy and r['budget']==b)) for b in (250,1000,2000)])
