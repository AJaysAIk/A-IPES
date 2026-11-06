# A-IPES-V

Specification-aware runtime verification for agentic systems.

A-IPES-V is a post-dissertation research extension of A-IPES. It asks:

Under a limited intervention budget, can probe selection prioritize evidence that is informative about explicit safety-property violations as well as unknown runtime policy behaviour?

The extension is motivated by verification and assurance of learning-enabled autonomous systems. It does not claim to formally prove an agent safe. Instead, it turns a small set of transition-level safety requirements into executable runtime monitors and adds specification information to the A-IPES acquisition objective.

## What is new

Original A-IPES scores candidate probes using outcome information, policy information, boundary proximity and novelty.

A-IPES-V adds two terms:

- Specification information: entropy over the safety-violation signatures predicted by the current hypothesis space.
- Expected violation: the posterior fraction predicting at least one monitored safety-property violation.

Conceptually:

    A-IPES-V score
      = A-IPES score
      + lambda_spec * H(predicted safety-violation signatures)
      + lambda_risk * P(predicted specification violation)

This preserves the original policy-identification objective while explicitly preferring interventions that can distinguish safety-relevant hypotheses.

## Executable safety specifications

The pilot monitors four properties over policy-state transitions:

1. supplier approval requires verified evidence;
2. purchase authorisation requires prior supplier approval;
3. publication requires verified evidence;
4. resource calls must not exceed five.

These are transparent transition monitors. They are not temporal-logic proofs, model checking, or whole-agent safety guarantees.

## Pilot benchmark

The synthetic pilot contains one safe tool and four tools capable of violating a monitored property. It compares specification_active, policy_active, and seeded random intervention selection.

Primary pilot outcomes are violation detection, specification coverage, and probe index of the first observed violation.

Run from the repository root:

    python -m pip install -e '.[dev]'
    python -m pip install -e extensions/aipes_v
    python -m pytest -q extensions/aipes_v/tests
    python extensions/aipes_v/scripts/run_demo.py

To save raw rows:

    python extensions/aipes_v/scripts/run_demo.py --output results/aipes_v_pilot.csv

## Research interpretation

A positive pilot would mean that adding explicit safety specifications helps allocate scarce behavioural tests toward safety-relevant uncertainty in this controlled state model. It would not establish formal verification, deployed MCP safety, robustness to stochastic agents, or generalisation to unseen tools.

Natural next steps are temporal specifications, stochastic transition models, counterexample-guided probe selection, integration with real MCP/tool traces, and comparison with established runtime-verification or model-checking baselines.

## Relationship to the dissertation

A-IPES-V keeps the dissertation's central idea, adaptive evidence acquisition under a fixed intervention budget, but changes the acquisition target from policy identification alone to policy identification plus explicit safety-property evidence.

That makes the extension a bridge from empirical runtime characterisation toward specification-driven assurance while keeping the scientific claims narrow and testable.

## v0.5 bounded temporal experiment

See [frozen protocol](V05_PROTOCOL.md) and [measured findings](V05_RESULTS.md).
The finite-trace adapter tests grant/revoke/use histories against an independent
monitor, response-information acquisition, random probing, and a finite-model
counterexample-guided baseline. Saved rows and full query audits are under
`results/v05/`. Specification weighting showed no incremental detection advantage
over response entropy in this experiment. This is not the unchanged v0.4 selector
or a claim of general temporal verification.

The [verified v0.4 findings](V04_RESULTS.md) include CI provenance and a matching
local raw-row reproduction. First-probe misses are confined to the conjunction
context; the three single-context families each detect 20/20 at budget 1.
