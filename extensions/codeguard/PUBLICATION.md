# Integration and publication provenance

This copy was integrated into A-IPES under `extensions/codeguard` after the local pilot. The parent dissertation implementation and archived results are unchanged.

The original pilot used the separate code-agent-security-eval working directory. This directory retains its self-contained package structure so dependencies and commands do not alter the dissertation package. Run extension commands from this directory.

Publication changes: main extension README and parent navigation; local model paths replaced by `codeguard/models/qwen-coder-1.5b`; ephemeral scanner prefixes replaced by `recorded-scan/`. Only filesystem-location metadata changed in measured output files: predictions, classifications, source text, hashes of model weights and corpus, tokens, latency and experiment configuration remain as recorded. The frozen protocol was not edited. Original pre-normalisation file hashes follow.

```json
{
  "codeguard/configs/model.json": "d85d490bf43daf77f8123aa3370490d8aa0d892c2cb7e24c8f320c1422eb20b9",
  "codeguard/results/model.meta.json": "a84de5317acbc305b4ff1485e1583f93f7d1d998dcd8f7ef35a6ad6f2b3595af",
  "codeguard/results/smoke.meta.json": "1597af4e4cc3c9554472c828927d2e8ce242835f97a445188fbcb166b67df3a6",
  "codeguard/results/static.json": "805e10893ce526ddbb6093d5e8292dfcb7eb77507d45fa8a113d32d19e2bb4bd"
}
```

The integrity inventory was regenerated for this public copy. It is unsigned and is not a trusted attestation. All generated implementation and preparation were AI-assisted; no independent authorship or external evaluation is implied. Existing interview-preparation documents describe practice artifacts, not completed employment duties.

The extension's original scanner tests were run locally. The new GitHub workflow is supplied to repeat them; its remote result must be checked after pushing. Docker and native presentation software are outside this code publication's validation.
