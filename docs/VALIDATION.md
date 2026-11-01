# Publication validation

Validated on 27 September 2026, macOS arm64, Python 3.14.3, in a fresh virtual environment installed from `.[dev]`. Exact installed package versions are recorded in `requirements-tested.txt`; these are a tested environment snapshot, not a cross-platform lockfile.

- All 17 existing tests passed in 73.73 seconds.
- `pip check` found no broken requirements.
- The README smoke command completed successfully.
- A separate seed-0 run with the original budgets `1,2,3,5` reproduced all 20 strategy/budget rows in the archived `per_benchmark.csv`, across all columns, within numerical tolerance 1e-12.
- The full 30-world experiment and ablation were not rerun for publication. Their published outputs are the archived dissertation evidence.
- Python source, scripts, and tests were checked byte-for-byte against the source commit listed in PUBLICATION_PROVENANCE.md.
- Publication files were checked for common credential patterns, private remote addresses, machine-specific paths, and the student number; no matches were found. This is a bounded scan, not a security certification.
- The public PDF’s extracted text matches the source with only the administrative declaration page removed. All retained pages were rendered for visual review.

For the exact tested package versions on a compatible Python environment, install `requirements-tested.txt` before installing the project. The main quick-start instructions use the package’s declared dependency ranges.

## Core research CI added on 1 November 2026

The core workflow is `.github/workflows/research.yml`; CodeGuard retains its separate workflow. The core matrix installs the declared development dependencies on Python 3.10 and 3.12, checks dependency health and scientific imports, and runs the complete core test suite. Each job retains its resolved dependency list. This tests supported dependency resolution rather than claiming that the historical Python 3.14 snapshot is a portable lockfile.

New CLI integration tests run one development world at budget 1 in both `legacy` and `matched_full` modes. They verify all five CSV outputs, completed provenance and source hashes, matched prior fingerprints, active diagnostic traces, paired-analysis output and overwrite protection. The legacy case also checks six metrics for the four non-random strategies against the archived seed-0, budget-1 rows to absolute tolerance 1e-12. Resampling counts are deliberately small for smoke testing; these outputs are not inferential research evidence.

Local checks use the existing Python 3.14.3 environment (NumPy 2.5.3, pandas 3.0.6, SciPy 1.18.1, scikit-learn 1.9.1). The scientific preflight and `pip check` passed. The archived 600-row paired-input file passes validation. No full 30-world experiment was rerun, and no new performance headline is claimed. Hosted Linux matrix results must be assessed from the workflow runs; local validation alone does not establish those results.

The archived random baseline drew five probes before taking prefixes; a budget-1-only run draws one. NumPy sampling without replacement is not prefix-invariant in its requested size, so the random baseline is excluded from this bounded archive comparison. This pre-existing schedule dependence is not a PR #1 regression.

Local results for this change: the pre-existing regression suite passed 39 tests in 275.16 seconds; the final two CLI integration cases passed in 55.45 seconds. They were run separately (41 passing cases in total), not as a single combined invocation. Formatting and lint checks passed for the new test file, and the diff whitespace check passed. The first archive assertion incorrectly included the random schedule across different maximum budgets; it was corrected as explained above and both integration cases were rerun successfully.
