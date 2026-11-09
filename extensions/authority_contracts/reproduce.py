"""One-command tests, regeneration, replay and comparison of frozen evidence."""
import argparse
import gzip
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
out = args.output.resolve()
if out.exists():
    raise SystemExit('Choose a new output directory; existing evidence is preserved.')
for test_dir in (ROOT, ROOT / 'main-study'):
    subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(test_dir),
                    '-p', 'test_*.py', '-v'], check=True)
subprocess.run([sys.executable, str(ROOT/'main-study/run_study.py'), '--output', str(out)], check=True)
subprocess.run([sys.executable, str(ROOT/'main-study/verify_and_summarise.py'), str(out)], check=True)
recorded = ROOT/'main-study/results-01'
for name in ('prefixes.csv','runs.json','summary.csv','verification.json'):
    if (recorded/name).read_bytes() != (out/name).read_bytes():
        raise SystemExit('Reproduction differs from recorded evidence: '+name)
# Compare actual events, not zlib-version-dependent compression bytes.
with gzip.open(recorded/'actions.jsonl.gz','rb') as expected, gzip.open(out/'actions.jsonl.gz','rb') as actual:
    index = 0
    while True:
        left, right = expected.readline(), actual.readline()
        if left != right:
            raise SystemExit(f'Action audit differs at record {index+1}')
        if not left:
            break
        index += 1
assert index == 800000
left = json.loads((recorded/'provenance.json').read_text())
right = json.loads((out/'provenance.json').read_text())
# Python runtime is environmental provenance, not a measured outcome.
recorded_python, actual_python = left.pop('python'), right.pop('python')
if left != right:
    raise SystemExit('Protocol, source hashes or execution metadata differ.')
print(f'PASS: all frozen outcomes and 800,000 action events match; Python {recorded_python} -> {actual_python}.')
print('Wall-time measurements are preserved separately and intentionally not byte-compared.')
