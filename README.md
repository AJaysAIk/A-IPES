# A-IPES

**Adaptive Intervention Planning for Efficient Runtime Policy Identification in Model Context Protocol Agents**

MSc Artificial Intelligence dissertation research by **Ajay Sai Kummara**, Queen’s University Belfast, 2026.

[Read the dissertation](paper/A-IPES_Dissertation.pdf) · [Research notes](docs/RESEARCH_NOTES.md) · [Benchmark V2](docs/BENCHMARK_V2.md) · [Code map](docs/CODE_TRACEABILITY.md)

## Research question

When behavioural testing is expensive, which intervention should an agent-assurance system perform next to identify an unknown runtime policy?

A-IPES selects probes sequentially under a fixed intervention budget, combining outcome information, policy information, boundary awareness, and behavioural novelty. This repository contains the Python implementation, controlled policy-state simulator, evaluation scripts, tests, and recorded experimental evidence.

## Main finding

Adaptive selection has a **budget-dependent advantage**: passive characterisation performs better at budget 2, the methods are close at budget 3, and A-IPES performs better at budget 5. The following means come from 30 paired, independently generated Benchmark V2 worlds:

| Budget | Passive recall | A-IPES recall | Passive policy exact match | A-IPES policy exact match |
|---|---:|---:|---:|---:|
| 1 | 0.872 | 0.878 | 0.924 | 0.925 |
| 2 | 0.944 | 0.912 | 0.968 | 0.947 |
| 3 | 0.966 | 0.964 | 0.984 | 0.977 |
| 5 | 0.966 | 0.974 | 0.984 | 0.989 |

At budget 5, both methods have zero observed false-positive rate in this benchmark. This is evidence from a controlled synthetic setting, not a guarantee for deployed agents. The passive baseline is literature-inspired, not an exact reproduction of an external system; its metadata prior also differs from the active method’s starting hypothesis space. See [research limitations](docs/RESEARCH_NOTES.md).

## Quick start

Requires Python 3.10 or newer. No API keys or external model services are needed.

```bash
git clone https://github.com/AJaysAIk/A-IPES.git
cd A-IPES
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q

# Small evaluation: one world, two budgets
python scripts/run_benchmark_v2.py --benchmark-seeds 0 --budgets 1,2 --output-dir results/local_smoke
```

On Windows, activate the environment with `.venv\Scripts\activate`.

## Reproduce the main experiments

```bash
# Defaults: benchmark seeds 0–29, budgets 1,2,3,5, probe seed 0
python scripts/run_benchmark_v2.py --output-dir results/local_benchmark_v2
python scripts/analyse_benchmark_v2.py --input results/local_benchmark_v2/per_benchmark.csv --output results/local_benchmark_v2/paired_active_vs_passive.csv

# Defaults: benchmark seeds 0–29, budgets 2,5, probe seed 0
python scripts/run_acquisition_ablation.py --output-dir results/local_ablation
python scripts/analyse_acquisition_ablation.py --input results/local_ablation/per_benchmark.csv --output results/local_ablation/paired_full_vs_ablated.csv
```

Full experiments are more expensive than the smoke run. Recorded results are in `results/benchmark_v2_30/` and `results/acquisition_ablation_30/`; they include summaries, per-world metrics, paired analyses, world manifests, and selected probes. Large per-trajectory `raw.csv` files are omitted and can be regenerated with the commands above.

## Repository guide

| Path | Purpose |
|---|---|
| `src/ipes_guard/policy_active.py` | Hypothesis space, acquisition function, adaptive probe selection |
| `src/ipes_guard/benchmark_v2.py` | Generated benchmark worlds and paired strategy evaluation |
| `src/ipes_guard/acquisition_ablation.py` | Acquisition component ablations |
| `scripts/` | Experiment runners and statistical analysis |
| `tests/` | Core behaviour, benchmark, and ablation tests |
| `results/` | Recorded dissertation experiment outputs |
| `paper/` | Public dissertation copy |
| `docs/` | Protocols, baseline definitions, traceability, and limitations |

The `ipes-guard` package name and earlier IPES terminology are retained for compatibility. Earlier protocol documents describe the project’s development; the Benchmark V2 results and research notes define the scope of this release.

## Validation

All **17 tests pass** in the publication environment. A seed-0 reproduction with all four budgets matches the archived metrics for all 20 strategy/budget combinations. See [validation details](docs/VALIDATION.md) and [tested dependencies](requirements-tested.txt). The complete 30-world experiments were not rerun for this release.

## Research status and citation

This is an MSc dissertation research prototype, not a peer-reviewed publication or a production security system. See [CITATION.cff](CITATION.cff) for citation metadata and [publication provenance](docs/PUBLICATION_PROVENANCE.md) for the source snapshot and public-copy changes.

Released under the [MIT License](LICENSE). See [RIGHTS.md](RIGHTS.md) for third-party rights and citation guidance. Security reporting guidance is in [SECURITY.md](SECURITY.md).
