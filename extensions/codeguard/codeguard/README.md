# A-IPES CodeGuard: measured defensive pilot

10 October 2026. A reproducible extension exploring budgeted reliability identification for a **source-text review component**. This is not an autonomous coding agent, production defence, or poisoned-model experiment. Implementation and writing were developed with AI assistance; the presenter must review, reproduce and understand the work before claiming personal mastery.

## What actually ran

- 144 inert Python source snippets: 18 base families, safe/vulnerable pairs, 4 representations. Nine development families and nine held-out families; siblings never cross the split.
- Real local MLX Qwen2.5-Coder-1.5B-Instruct 4-bit inference, pinned immutable revision and file hashes. One greedy response per sample; 144/144 valid responses.
- Semgrep 1.178.0 Community Edition with three checked-in taint rules; all 144 files scanned.
- Eight selection strategies, four budgets, 100 selection seeds on cached development responses. The 100 seeds are not independent model or dataset replications.
- Main held-out result: model 10/36 vulnerabilities detected, 0/36 safe cases flagged. Semgrep and OR hybrid: 36/36 detected, 4/36 safe cases flagged. The hybrid provides **no benefit over Semgrep alone** here.
- At budget 24, adaptive full Brier 0.2679 versus fixed 0.2540 (lower better). Adaptive transfer did not improve the primary endpoint. See full results and all ablations in `results/summary.json`.

## Reproduce without a model download

Run from `A-IPES/extensions/codeguard` in a Python 3.11 environment:

```sh
python -m pip install -e '.[dev,codeguard,semgrep]'
python -m codeguard validate
python -m pytest -q
python -m codeguard analyse
python -m codeguard.demo
```

Analysis uses recorded real model responses and scanner outputs. It makes **no new model calls**. The terminal demonstration is explicitly a replay, never a staged live inference. Replaying analysis replaces derived summaries/figures; preserve an archive if comparing runtime measurements.

## Repeat live local inference on Apple Silicon

```sh
python -m pip install -e '.[local-model]'
python codeguard/download_model.py
python -m codeguard model --model-config codeguard/configs/model-local.json --output codeguard/results/repeat-model.jsonl
python -m codeguard static --output codeguard/results/repeat-static.json
```

The downloader verifies the original revision and all file hashes, writing a machine-local path configuration without changing the recorded original. It downloads about 1 GB; no API key is required. MLX needs an accessible Metal GPU. A normal local terminal may be required when an application sandbox cannot access Metal. Use a separate results directory and manifest copy for a fresh analysis comparison; the analysis command reads `model.jsonl`, `model.meta.json` and `static.json` alongside its manifest's parent directory. Do not replace primary results to obtain a preferred story.

`model` resumes an existing output only when recorded protocol, model, prompt and corpus hashes match. Decode failures remain failures. No fixture source is executed. Semgrep writes ephemeral text files solely for scanning. It never runs those files.

## Docker: supplied, not tested on this host

```sh
docker build -f codeguard/Dockerfile -t codeguard-pilot .
docker run --rm --network none codeguard-pilot validate
docker run --rm --network none codeguard-pilot analyse
```

The CPU image supports cached analysis and static review, not MLX inference. Docker is unavailable on the author host, so neither build nor container execution is verified. The base is version-tagged, not digest-locked; the observed macOS dependency list is evidence, not a portable lock. Semgrep integration and analysis were tested directly on macOS. The image does not execute the toy corpus.

## Reading order

1. `docs/PROTOCOL.md`: frozen questions, budgets, metrics and limitations.
2. `docs/FINDINGS.md`: complete interpretation, costs and all ablations.
3. `docs/DUTY_EVIDENCE.md`: honest mapping to the eight QUB duties.
4. `docs/LEARNING_AND_DEMO.md`: explanation, demonstration and interview practice.
5. `docs/LITERATURE.md`: primary literature and implementation links.
6. `results/model.jsonl`, `results/static.json`, `results/acquisition.csv`: raw/derived evidence.

## Security and provenance boundary

SHA-256 hashes detect mismatches against a trusted reference; they are not signed attestations or proof of authorship. No credential, remote target, malicious payload execution, automatic merge, training-data poisoning, proprietary API experiment, outreach email, or publication is included. The synthetic trigger demo is a programmed rule simulation, labelled separately from actual LLM measurements.
