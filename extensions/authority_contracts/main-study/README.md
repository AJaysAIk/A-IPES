# Authority-contract comparison: completed synthetic study

The study completed 400 runs and 800,000 actual action calls across document and
purchase workflows, four strategies, ten fixtures and ten seeds. All 1,200 budget
prefix rows passed a separate replay. A second run matched the deterministic
artifacts byte for byte. Seven study tests and five feasibility tests pass locally.
No CI or independent external replication is claimed.

## Read first

- `TECHNICAL_REPORT.md`: editable report; the supplied PDF is the presentation copy.
- `PROTOCOL.md`: design fixed and locally hashed before purchase selector outcomes.
- `results-01/summary.csv`: per-fixture detections and legitimate-operation counts.
- `results-01/verification.json`: scope and size of the completed replay.
- `results-01/actions.jsonl.gz`: every actual action, phase and monitor verdict.
- `results-01/provenance.json`: protocol and implementation hashes.

## Main result and stop decision

The fixed public-contract suite catches all planted faults at the earliest
reported budget (250 calls). BBC catches all by 1,000 calls, but its incremental
detection benefit over learning alone is confined to the document expiry fault.
All purchasing first detections are in the learning phase. These fixtures are too
shallow to justify a claim that a new acquisition method is needed.

The protocol's saturation stop rule is reached. Do not add methods or retune this
evaluation to produce a preferred winner. Use the report and counterexamples to
seek research critique, then design any deeper composition/partial-observation
study separately. This is a methodological writing sample and evidence package,
not a demonstrated ATC extension or a publication acceptance.

## Reproduce

Install the parent `requirements.txt` in an isolated Python environment. From this
directory:

```sh
python -m unittest discover -s . -p 'test_*.py' -v
python run_study.py --output /tmp/new-authority-results
python verify_and_summarise.py /tmp/new-authority-results
```

The experiment refuses existing result directories. Compare `prefixes.csv`,
`actions.jsonl.gz`, `runs.json` and `provenance.json` to the recorded files.
Wall times are expected to vary and are excluded from byte comparisons.

The verification uses the service and monitor in a separate pass, not an
independently developed judge. Protocol freezing is a local hash, not external
preregistration. The purchasing outcome reservation is prospective but synthetic;
there is no independent population sample. Models returned by approximate
oracles are not certified correct, and model checking is bounded to depth six.
