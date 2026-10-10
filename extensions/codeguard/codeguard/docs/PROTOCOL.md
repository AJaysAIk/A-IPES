# CodeGuard pilot protocol v1

Frozen before main inference, 10 October 2026. Defensive, text-only evaluation; no fixture execution, remote target, credentials, package installation by model, or automatic merge. This is an A-IPES-inspired extension, not the unchanged dissertation algorithm or a deployed agent.

## Questions and predeclared endpoints
1. Does a frozen local code reviewer change class-specific detection under approved source transformations? Measure original/transformed paired detection, safe-case FPR, coverage and conditional evasion.
2. Can adaptive selection learn its empirical correctness profile at lower query budgets than random and fixed stratified selection? Primary: held-out Brier score at budgets 6, 12, 24, 48; secondary: distinct failing families found. No promise of advantage. Profile cells are weakness class x transformation, aggregate vulnerable and safe cases equally. Feedback uses ground truth only for queried examples, an explicitly oracle-assisted offline setting.
3. Does a lightweight OR hybrid of model plus checked-in Semgrep improve detection, and at what false-positive/latency cost? Primary: paired recall difference and safe-case FPR on held-out families. Retain scanner findings, never let LLM remove them. Errors are explicit, never clean negatives.

## Corpus
Three weaknesses: SQL injection, shell command injection, path traversal. Six manually designed structural templates per class; vulnerable/safe pairs, four variants (original, scope-limited renaming, formatter roundtrip, helper indirection): 144 samples. Development templates 0,1,2; held-out templates 3,4,5. All siblings remain grouped. Handcrafted narrow examples and single annotator are important limits; template counts are not independent real projects. The general threat is developer-controlled source representation; no model poisoning is performed.

Transform validation: AST equality for formatter; inverse-renaming AST equality for local-variable renaming under excluded reflection; helper wrapping moves the unchanged function body to a helper, preserving argument and return flow within these restricted fixtures. Static structural checks verify the unchanged body, no executable tests of unsafe samples. Record that static structural checks are not a general proof of semantic equivalence.

## Frozen configuration
MLX Qwen2.5-Coder-1.5B-Instruct 4-bit community quantisation, immutable revision and file hashes recorded at download; greedy decoding, fixed prompt, bounded output. Prompt calibration only on two independent smoke examples outside the corpus. Class labels/filesystem paths withheld; model receives only source, fixed scope assumptions, and requested JSON contract. No test-prompt tuning.

Static rules chosen from documented sink/safety constructs before model outcomes. OR hybrid uses union of per-class findings. All runs retain raw outputs, source/prompt/model/rule hashes, tokens, latency and status. No retries to obtain a preferred answer; interrupted runs can resume only with matching manifests. Local code fixtures are text data only.

## Adaptive acquisition
Beta(1,1) correctness prior per class x transform cell. Compare random without replacement; fixed round-robin stratification; adaptive expected mutual information about cell correctness; adaptive uncertainty about below-0.8 reliability (policy-information); full A-IPES-inspired score = outcome information + 1.5 policy information + .2 boundary + .1 novelty. Normalise components to [0,1] within available pool. Boundary score prioritises posterior mean close to 0.8. Novelty penalises selecting an already probed base family. All use identical priors, pools and budgets; weights/thresholds fixed before outcomes.

Replay only development outcomes for acquisition; evaluate inferred cell probabilities against held-out outcomes inaccessible to selector. 100 selection seeds quantify selection variability only, NOT 100 independent models or datasets. Report bootstrap uncertainty by held-out base family, preserving siblings. Discovery on development pool is secondary, not held-out generalisation. An exhaustive cached response matrix has an upfront cost reported separately; replay budgets are simulated audit budgets, not actual wall-time savings demonstrated live.

Ablations remove policy information, boundary and novelty individually; include outcome-only. Report every strategy and budget; do not select the favourable one as primary after seeing results. For full-vs-fixed held-out Brier difference at B=24 report family-cluster bootstrap interval. Intervals are exploratory with nine held-out families.

## Defence cost
Measure static-only batch duration including process startup; LLM per-sample wall time and tokens. Sequential hybrid estimate = actual LLM time + batch static time, clearly labelled an estimate, not separately timed end-to-end. No speed claim based on model calls alone. AST canonicalisation can be evaluated as a representation robustness condition; it is not claimed to defeat injection or interprocedural evasion.

## Claim constraints
Single small quantised model, Python toy corpus, binary/code-review component rather than tool-using agent. No backdoor-free, production-safe or general superiority claim. No proprietary API result without authorised access and terms review. Duty mapping uses 'implemented and evaluated', 'practised', 'illustrated only', 'not done' accurately. Synthetic backdoor smoke tests, if provided, are NOT poisoned-LLM research.
