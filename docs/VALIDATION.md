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
