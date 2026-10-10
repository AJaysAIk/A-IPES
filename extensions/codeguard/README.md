# A-IPES CodeGuard extension

Post-dissertation defensive research pilot, 10 October 2026. This self-contained Python project applies A-IPES's budgeted intervention philosophy to a source-text code reviewer's reliability. It is a new probabilistic adaptation, not the unchanged dissertation algorithm.

## Measured findings

144 inert Python samples; 18 base families; 9 development and 9 held-out families. Real local MLX Qwen2.5-Coder-1.5B-Instruct community 4-bit inference, pinned revision and artifact hashes. SQL injection, command injection and path traversal; original, renamed, formatted and helper representations.

| Held-out reviewer | Detected vulnerabilities | Safe cases flagged |
|---|---:|---:|
| Local model | 10/36 | 0/36 |
| Semgrep | 36/36 | 4/36 |
| OR hybrid | 36/36 | 4/36 |

The hybrid adds no benefit over Semgrep alone on this narrow corpus. Full adaptive selection also underperforms fixed coverage at the predeclared budget-24 Brier endpoint (0.2679 versus 0.2540; lower is better). These results are retained rather than replaced by a favourable secondary metric. This is a single-model toy-corpus pilot, not a production assurance claim.

## Run from this extension directory

```sh
git clone https://github.com/AJaysAIk/A-IPES.git
cd A-IPES/extensions/codeguard
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev,codeguard,semgrep]'
python -m codeguard validate
python -m pytest -q
python -m codeguard analyse
python -m codeguard.demo
```

Analysis and demonstration use recorded real-model outputs without new inference. Reviewed source is never executed. Model weights and virtual environments are excluded from Git. To repeat MLX inference on Apple Silicon, follow the [detailed reproduction guide](codeguard/README.md).

## Evidence and method

- [Frozen protocol](codeguard/docs/PROTOCOL.md)
- [Complete findings, all ablations and overhead](codeguard/docs/FINDINGS.md)
- [Raw model responses](codeguard/results/model.jsonl), [Semgrep results](codeguard/results/static.json), [summary](codeguard/results/summary.json)
- [Corpus manifest](codeguard/corpus/manifest.jsonl) and [selection replay results](codeguard/results/acquisition.csv)
- [Validation](codeguard/docs/VALIDATION.md) and [publication provenance](PUBLICATION.md)
- [Literature reconnaissance](codeguard/docs/LITERATURE.md)
- [Learning and demo guide](codeguard/docs/LEARNING_AND_DEMO.md)

41 local tests passed including Semgrep integration. The Docker recipe is supplied but its build/run is unverified. The nested historical six-fixture harness remains available separately; its mock results are not LLM results. See [historical harness documentation](LEGACY_HARNESS.md).

## Boundaries

AI-assisted implementation and preparation. No autonomous agent, real poisoned LLM, proprietary API study, signed attestation, published paper or industry outreach is claimed. Hashes provide unsigned integrity checks. The 100 selector seeds do not represent independent model or dataset replications. See the findings report for label, prompt, correlation and generalisation limitations.

Licensed under [MIT](LICENSE). [A-IPES dissertation](../../README.md).
