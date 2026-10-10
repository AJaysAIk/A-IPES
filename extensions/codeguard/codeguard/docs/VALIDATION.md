# Validation record - 10 October 2026

- Full local suite, including real Semgrep integration: **41 passed in 3.21 seconds** (Python 3.11.15, installed scanner on PATH).
- Ruff lint: passed. Ruff format check: 40 files already formatted at final source check.
- Corpus validation: 144 unique IDs, hash checks, parsed ASTs and family split invariants.
- Real inference: 144/144 valid main outputs, no output retries. Separate two-example smoke run.
- Static scan: 144/144 paths accounted for, no scan errors; 84 findings across both splits.
- Replay analysis: 8 strategies x 100 seeds x 4 budget snapshots = 3,200 rows, with eight seed-zero traces.
- Recorded demonstration executed successfully; no reviewed source executed.
- Model/source/protocol/corpus identities are preserved in metadata and the integrity manifest. The latter is unsigned, not a trusted attestation.
- Docker build/run, proprietary API experiments, real poisoned LLMs and native PowerPoint application playback were not tested.

The model required Metal access outside the application sandbox. Semgrep also ran outside it because the sandbox blocked certificate-initialisation access. These are local runtime constraints, not evidence that the source corpus needs execution or network access.

Source refinements after the frozen main run: CLI output defaults separated to avoid a static command overwriting model output; downloader made pinned and portable without modifying original run metadata; synthetic-demo string formatting; documentation and replay demonstration. Model prompt, corpus, acquisition settings and main measurements were not tuned after viewing held-out results.
