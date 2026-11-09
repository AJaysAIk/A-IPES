# Authority contracts under a fixed test budget

A reproducible, AI-assisted synthetic follow-up to A-IPES-V. This package contains
**400 runs, 800,000 actual service actions, 1,200 prefix outcomes and 12 tests**.

## Read the evidence

- [Five-page working report](reports/authority-contract-evidence-report.pdf)
- [Editable report](main-study/TECHNICAL_REPORT.md)
- [Fixed protocol](main-study/PROTOCOL.md)
- [Per-fixture results](main-study/results-01/summary.csv)
- [Replay verification](main-study/results-01/verification.json)
- [All action records (compressed JSONL)](main-study/results-01/actions.jsonl.gz)
- [Original source hashes and environment provenance](main-study/results-01/provenance.json)
- [Concrete development counterexamples](CASE_STUDIES.md)

## Main finding

The six-trace public-contract suite detects every planted fault within the first
reported budget of 250 calls. Monitored L* with black-box checking reaches the
same coverage by 1,000 calls. Its incremental detection advantage over monitored
L* without checking is confined to the document-expiry fixture. Every purchasing
first detection occurs during learning. These shallow faults do not establish a
need for a new acquisition method. The prespecified saturation stop rule applies.

This is a controlled comparison and failure analysis, not a novel verification
algorithm, an ATC reproduction, a deployed-agent safety guarantee or a publication.

## Reproduce from any directory

Create a Python environment and install `requirements.txt` from this directory.
Then run:

```sh
python extensions/authority_contracts/reproduce.py --output /tmp/authority-new-results
```

From a standalone checkout, adjust the script path accordingly. The command runs
both test suites, regenerates all experiments, replays every actual action, and
compares every frozen prefix and event with the supplied evidence. Existing output
directories are rejected. Runtime version and wall time are compared separately
from scientific outcomes. Gzip content is compared after decompression so changes
in compression libraries do not masquerade as experimental differences.

## Design and claim boundaries

The document service uses SQLite; purchasing is separately implemented in Python.
Both are local deterministic fixtures with deliberately injected faults. AALpy
2.0.0 supplies the L* learner and BBC wrapper; the property oracle and tool adapters
are custom, and checking is bounded to depth six. All real membership, equivalence
and validation actions count toward the same cap; model-only work is separate.

The purchasing selector outcomes were prospectively reserved under a locally
hashed protocol, not external preregistration. Seeds vary ordering and do not
constitute independent implementation samples. Replay uses the service and public
monitor in a separate pass, not an independently developed judge. A returned model
from an approximate oracle is not certified correct. No LLM agents are evaluated.

The original November 6 experiment sources and their hashes are retained unchanged.
This publication adds packaging and CI; it does not retune the study. Original
wall-time records are included as machine-specific provenance, not speed claims.
CI status must be checked independently before claiming remote reproduction.
