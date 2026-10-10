# A-IPES CodeGuard: pilot findings

Ajay Sai Kummara | QUB RA interview preparation | 10 October 2026

## 1. Research claim and scope

This is a defensive, source-text review experiment applying A-IPES's budgeted intervention philosophy to a frozen code reviewer's reliability. It is an extension developed after the dissertation, not a re-run of the original method. It evaluates one public local model artifact, three weakness classes and narrow handcrafted Python snippets. There is no autonomous coding agent, real-world exploit execution, poisoned LLM or proprietary API evaluation.

Two useful results emerged: harmless representation changes sometimes changed the model's security verdict, and simple static checks recovered missed vulnerabilities with measurable false positives. The A-IPES-inspired selector did not improve the primary held-out reliability-estimation metric. All outcomes, including unsuccessful transfer and unchanged ablations, are reported.

## 2. Design fixed before the main run

The frozen protocol is `docs/PROTOCOL.md`; its SHA-256 appears in the model metadata. Three weaknesses x six structural families x two labels x four representations gives 144 source samples. There are 72 development and 72 held-out samples; safe/vulnerable pairs and all transformed siblings stay within one family and split. Nine held-out families contain 36 vulnerable and 36 safe variants. These are correlated variants, not 72 independent projects.

The three transformations are scope-limited renaming, AST formatting, and helper indirection. Formatting is AST-equal, renaming reverses to the original AST, and helper wrapping preserves the original body and argument flow under restricted assumptions. The checks do not constitute general semantic equivalence proofs. The renamed input is explicitly covered by the prompt's `value/item` untrusted-input assumption. No unsafe fixture is executed.

The model is MLX community Qwen2.5-Coder-1.5B-Instruct 4-bit, revision b3252a2f97102b1fb1571fec2c9b27219a8536be. Model file hashes, chat template, prompt hash, greedy decoding, seed 17 and a 128-token output cap are recorded. The model receives source only, with a fixed prompt and explicit safety assumptions; sample IDs, labels and filenames are withheld. All 144 responses were valid. Two independent smoke calls are separate from the 144 main calls. The prompt includes an all-false JSON example, which may bias this small model; no alternative prompt was tested and no prompt-independent capability claim is warranted.

Semgrep 1.178.0 used three checked-in taint rules, chosen before observing model outcomes. Labels come from fixture design, not scanner agreement. The scanner and corpus share narrow constructs, so perfect vulnerable-case recall is unsurprising and must not be generalised. Community Edition limitations and parameter-as-source assumptions matter. A hybrid returns each class's Boolean union; malformed model outputs escalate instead of becoming clean negatives.

## 3. Held-out security results

Metrics below use the labelled target class on each sample. All-class micro results are also retained in the machine-readable summary, but have a different negative denominator and should not be substituted for safe-case FPR.

| Reviewer | Detected / vulnerable | Flagged / safe | Recall | Safe-case FPR | Precision |
|---|---:|---:|---:|---:|---:|
| Local model | 10 / 36 | 0 / 36 | 27.8% | 0.0% | 100.0% |
| Semgrep | 36 / 36 | 4 / 36 | 100.0% | 11.1% | 90.0% |
| OR hybrid | 36 / 36 | 4 / 36 | 100.0% | 11.1% | 90.0% |

A high precision alone is misleading: the model misses 26 vulnerabilities. Hybrid recall increases by 72.2 percentage points relative to the model, with an exploratory family-bootstrap interval of 50.0 to 91.7 points. Safe-case FPR rises 11.1 points (interval 0.0 to 33.3). These intervals use only nine held-out clusters, conditional on this corpus. They do not establish population-wide performance.

**The hybrid has no incremental detection or precision benefit over Semgrep alone.** For this benchmark, the simpler scanner is the more economical choice. A future hybrid needs evidence of complementary errors on broader code before its extra complexity is justified.

All four safe flags are sibling variants of one path family using a fixed-path lookup dictionary. Conservative taint propagation confuses an untrusted dictionary key with an untrusted path value. They are four false-positive variants but one underlying family, not four unrelated bugs. No rules were tuned after seeing these held-out outcomes.

## 4. Representation sensitivity

Held-out recall by weakness and representation follows. Each cell has only three vulnerable examples; fractions are more informative than broad percentage claims.

| Weakness | Original | Renamed | Formatted | Helper |
|---|---:|---:|---:|---:|
| SQL injection | 2/3 | 0/3 | 2/3 | 0/3 |
| Command injection | 0/3 | 0/3 | 0/3 | 0/3 |
| Path traversal | 2/3 | 0/3 | 2/3 | 2/3 |

For SQL, both originally detected examples became missed after renaming or helper wrapping. For path traversal, both originally detected examples became missed after renaming. Those conditional evasion rates are 2/2, with tiny denominators. Command injection has no originally detected examples, so conditional evasion is undefined, not zero. Overall missed-vulnerability rate and transformation-induced evasion are different metrics.

This is inference-time representation sensitivity. It does not show prompt injection, malicious instructions, model poisoning, or a backdoor. The demonstration selects one recorded pair after evaluation for illustration; the aggregate table remains the evidence.

## 5. The A-IPES bridge

| Original dissertation object | CodeGuard adaptation | What changes |
|---|---|---|
| Intervention/probe | Labelled code representation to review | Source formatting/structure replaces runtime-state manipulation |
| Runtime observation | Three Boolean security classifications | Correctness requires a labelled offline oracle |
| Finite hidden runtime policy | Reliability profile across class x representation | A statistical summary, not recovery of model internals |
| Version-space reduction | Beta-Bernoulli posterior update | Probabilistic cell estimate replaces exact finite elimination |
| Intervention budget | Number of revealed cached development reviews | Replay budget does not prove live monetary savings |
| Active/passive comparison | Adaptive vs random vs fixed stratified queries | Equal priors, pools and budgets in this extension |

Each of 12 cells starts Beta(1,1). A correct target-class review increments alpha and an incorrect one increments beta; the posterior mean is alpha/(alpha+beta). Outcome information estimates uncertainty reduction about correctness probability. Policy information estimates uncertainty reduction about whether that probability is below 0.8. The full score combines normalised outcome information, 1.5 x policy information, 0.2 x boundary proximity and 0.1 x family novelty.

The 0.8 threshold is a predeclared experimental choice, not a recognised deployment safety threshold. Accuracy aggregates safe and vulnerable cases equally, so it can conceal a sensitivity/specificity imbalance. A richer future profile should model false negatives and false positives separately.

## 6. Adaptive experiment and all ablations

A selector sees public candidate metadata and queried feedback only. It cannot read unqueried correctness or held-out outcomes. The exhaustive response matrix was computed once; 100 selection seeds replay budgets 6, 12, 24 and 48. The same frozen model responses are reused, so seeds measure selection variability rather than independent inference replications.

The endpoint is held-out Brier loss for predicted target-class correctness: average squared error between predicted probability and observed correctness. Lower is better. The table reports the mean over selection seeds. The primary contrast is full minus fixed at budget 24.

| Strategy | B=6 | B=12 | B=24 | B=48 |
|---|---:|---:|---:|---:|
| random | 0.2547 | 0.2560 | 0.2531 | 0.2350 |
| fixed | 0.2576 | 0.2637 | 0.2540 | 0.2341 |
| outcome_only | 0.2568 | 0.2637 | 0.2540 | 0.2341 |
| policy_only | 0.2568 | 0.2637 | 0.2673 | 0.2558 |
| full | 0.2583 | 0.2643 | 0.2679 | 0.2558 |
| no_policy | 0.2583 | 0.2643 | 0.2545 | 0.2352 |
| no_boundary | 0.2583 | 0.2643 | 0.2675 | 0.2540 |
| no_novelty | 0.2568 | 0.2637 | 0.2671 | 0.2558 |

At budget 24, full is 0.2679 versus fixed 0.2540: difference +0.0140, exploratory paired family-bootstrap 95% interval +0.0005 to +0.0286. The interval is conditional on the fixed development pool and averages seeds within each held-out family. Only nine held-out families are resampled. This is evidence against an advantage on this endpoint in this pilot, not a universal ranking.

As an explanatory reference, always predicting 0.5 gives Brier 0.25 for any binary labels. At budget 24 all reported strategies are worse than that reference; at budget 48 fixed reaches 0.2341 while full remains 0.2558. The 0.5 reference is a post-run explanatory calculation, not a newly declared primary endpoint.

The full selector found 7.23 distinct failing development families on average at budget 24, compared with fixed 6.70 and random 6.73. This is a secondary descriptive result on the development pool, not a held-out gain or evidence of saved live calls. Do not substitute it for the unfavourable primary result.

Removing policy information reduces Brier to 0.2545 at budget 24. Removing boundary or novelty does little. A plausible explanation is objective mismatch: selecting for certainty around a reliability threshold can differ from estimating probabilities well across all cells. This mechanism was not separately established. Small correlated data, acquisition bias and development/test differences are alternative explanations. All eight strategies and all budgets remain visible.

## 7. Duty 5: defence and overhead

For the 144 main reviews, inference elapsed time sums to 217.186 seconds, excluding model load. Median per-review latency is 1.502 seconds and p95 is 1.764 seconds. Input tokens total 27,370 and generated tokens 4,464. The separate smoke calls are not included in these totals. The pinned model's load duration is recorded in metadata.

The complete static batch took 3.880 seconds, including scanner startup. Sequential union processing is estimated as model time plus static batch: 221.066 seconds, about 1.79% above the model-only measured total. This is a sequential estimate, not a separately timed end-to-end pipeline or a repeated timing confidence interval. File preparation, model load and interactive application overhead are outside that sum. Adding the model to a static-only workflow would instead increase cost substantially, with no accuracy benefit measured here.

The 800 selection runs (8 strategies x 100 seeds through maximum budget 48) took 12.226 seconds during the recorded analysis. This is offline replay overhead, not part of model inference or the static batch; hardware and workload differ from deployment. Future work should measure repeated cold/warm timing, peak memory, throughput and end-to-end integration.

Duty 5 is practised through real review-time checks, measured detection/false-alarm outcomes and transparent overhead accounting. Hash manifests illustrate artifact integrity; signed attestation and anomaly detection are not implemented, and the job lists these as possible examples rather than requiring all in one pilot.

## 8. Reproducibility, validation and limits

Raw responses, scanner findings, manifests, prompts, model revision/hash metadata, selector traces, acquisition CSV, all ablations and plotting code are retained. Forty-one tests passed, including real Semgrep integration; formatting and lint checks passed. Tests cover corpus integrity, family splits, parser types, hand-counted metrics, selection feedback boundaries and the explicitly synthetic trigger comparison. The safe demo runs from cached real outputs without model access or execution of reviewed source.

A Docker recipe is supplied for CPU replay/static analysis. Docker is not installed on the author host, so container build/run is unverified. The base image is version-tagged rather than digest-locked, and the macOS observed-dependency snapshot is not a portable lockfile. The local runtime was tested; cross-platform identity of outputs is not promised.

Hashes are unsigned integrity evidence, not proof of trusted origin or a signed attestation. The implementation and preparation were AI-assisted. The candidate should reproduce, inspect and explain them before claiming ownership of decisions or expertise. No paper submission, proprietary-model result, trained backdoor, group-repository contribution, partner outreach or completed demo video is claimed.

The most important limits are a tiny manually labelled corpus with structural similarity across train/test families; only one small quantised model and one prompt; no independent annotator; no repeated stochastic inference; nine held-out clusters; an oracle-assisted selector; and source review rather than a full tool-using agent. Narrow model performance must not be advertised as representative of all code assistants.

## 9. Next experiment, decided from the evidence

First independently audit labels and expand structurally distinct families. Freeze a second protocol and fresh holdout before testing new prompts, rules or selector settings. Compare a stronger local model and, with authorised access and applicable terms reviewed, a proprietary API. Separate sensitivity and specificity profiles and align acquisition utility with the actual assurance decision. Evaluate whether any LLM catches errors the static scanner misses. Only then extend the harness to a sandboxed agent workflow and a properly isolated research backdoor study.

## 10. Interview interpretation

Present one research line: A-IPES's question, method and budget-dependent dissertation findings, followed by this explicitly labelled transfer pilot. Acknowledge that passive beats active at dissertation budget 2 and that active does not win the CodeGuard primary endpoint. The contribution you can defend is the experimental design, measured failure analysis, practical defence comparison and reproducible evidence.

The full duty map and learning/demo script accompany this report. The candidate should say 'practised' where appropriate, not 'all duties completed'. For duty 8, the research note and demonstration are preparation artifacts, not evidence of publication or industry collaboration.

## References and evidence

QUB Candidate Information: https://hr.apps.qub.ac.uk/jobs/job_desc/26_113642.pdf

Original A-IPES archived Benchmark V2 and ablation CSVs: sibling A-IPES repository, results/benchmark_v2_30 and results/acquisition_ablation_30. These are dissertation evidence, not newly generated CodeGuard measurements.

Semgrep taint analysis: https://docs.semgrep.dev/writing-rules/data-flow/taint-mode/overview

MLX-LM implementation: https://github.com/ml-explore/mlx-lm

Original model card: https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct

Evaluated community conversion: https://huggingface.co/mlx-community/Qwen2.5-Coder-1.5B-Instruct-4bit

The broader reconnaissance log lists AgentDojo, TrojanPuzzle and BaxBench with explicit non-reproduction notes. External sources motivate methods; the numerical findings above come from local recorded experiments, not those papers.
