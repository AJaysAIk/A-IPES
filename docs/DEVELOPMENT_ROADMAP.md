# A-IPES development roadmap

Each work session should produce a tested improvement or a documented research decision. Dates record actual work; do not backdate commits or generate activity-only changes. Future entries are a queue, not scheduled automation.

## 2026-11-01 — Core research validation

- Review PR #1's identification diagnostics and matched-prior comparisons against current main.
- Add core CI on Python 3.10 and 3.12, separate from the existing CodeGuard workflow.
- Exercise both prior modes through the benchmark and paired-analysis CLIs, checking output schemas, provenance hashes, prior equality, diagnostic traces and overwrite protection.
- Clarify historical validation counts and the legacy-prior scope of the README results.
- Validation evidence and remaining limits are recorded in `VALIDATION.md`.

## Next work sessions, in priority order

1. **Validate benchmark inputs before computation.** Reject non-integral, non-positive and pool-exceeding budgets consistently at the API and CLI boundaries. Test that invalid runs do not leave misleading output directories.
2. **Make random schedules explicit.** Document maximum-budget dependence, and evaluate a versioned prefix-invariant random ordering without changing archived experiment semantics.
3. **Improve failed-run provenance.** Record failure status and partial outputs explicitly; test interrupted/failed runs without hiding the original error.
4. **Expose identification summaries.** Aggregate inconsistency and fallback rates by world and strategy, keeping them separate from predictive accuracy. Verify aggregates against raw rows.
5. **Design a fresh-world matched-prior evaluation.** Freeze seed lists, budgets, acquisition weights and analysis before running. Separate development and held-out worlds; report paired uncertainty and negative outcomes. A one-world CI run cannot substantiate a research claim.
6. **Assess a CodeGuard extension only against a concrete gap.** First inspect existing corpus, baselines and validation. Keep its evidence separate from A-IPES simulation results; do not imply hybrid or adaptive benefit where none was measured.

## Completion standard

Use only public repository material. For each substantive commit, record what changed, the checks actually run, and limitations. Keep generated bulk outputs and machine-specific environment paths out of commits. Merge only after relevant validation; preserve archived dissertation outputs and report new experiments separately.
