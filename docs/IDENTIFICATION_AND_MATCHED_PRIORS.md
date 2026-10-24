# Identification diagnostics and matched priors

The benchmark now distinguishes a single surviving hypothesis (`consistent`), multiple survivors (`ambiguous`), and an empty original-prior version space (`inconsistent`). These labels describe the specified hypothesis library, not real-world safety. Historical fallback predictions remain compatible and are explicitly flagged. Legacy posterior-size and information-gain fields must not be interpreted as sound posterior information after inconsistency.

Active selected-probe rows include a JSON diagnostic trace with observed states, survivor counts, acquisition components and seed. The trace budget describes the maximum active run; the outer row budget describes the evaluated prefix. Repeated rows are not independent tool fits.

## Equal starting information

`--prior-mode legacy` remains the default. It retains the metadata-filtered passive prior. `--prior-mode matched_full` gives active and passive methods the same full hypothesis library. Prior fingerprints make this equality inspectable. The simulator, fixed passive schedule and acquisition weights are unchanged.

`policy_exact_match` measures agreement between actual and predicted policy-violation-code tuples over evaluated cases, averaged within worlds and then across worlds. It is not whole-policy recovery. Zero observed false positives is not a population guarantee.

## Running and analysing

From the repository root, with the project dependencies available:

```sh
python scripts/check_research_environment.py
PYTHONPATH=src python -m pytest -q
PYTHONPATH=src python scripts/run_benchmark_v2.py --benchmark-seeds 0,1,2 --budgets 1,2,3,5 --prior-mode matched_full --output-dir results/matched_prior_example
```

The output directory must not already exist. Each run saves parameters, dependency versions, source hashes and completion status. Use a new directory for each run. The analysis script rejects duplicate, missing or non-finite pairs and mixed/unknown explicit prior modes. Historical files without a mode column are treated as legacy.

## Scope and evidence limits

The local development pilot used three previously used worlds, not a held-out evaluation. Its reported performance measures were unchanged between prior modes; this does not establish that prior choice never matters. Bulk pilot artifacts are not included in this change, so no new numerical headline is presented here. The simulation assumes exact observations and heuristic acquisition weights. Fresh-world evaluation, noisy inference, abstention, runtime enforcement and real MCP deployment validation require further work.
