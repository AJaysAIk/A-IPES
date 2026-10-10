# Literature and implementation reconnaissance

This is a compact preparation/research log, not a systematic review or reproduction of the cited papers. Consulted for the study guide and this extension, 9-10 October 2026.

| Source | Relevant mechanism | Design consequence | Limit |
|---|---|---|---|
| AgentDojo, https://arxiv.org/abs/2406.13352 and https://github.com/ethz-spylab/agentdojo | Tool-mediated prompt injection, utility/security jointly | Do not conflate secure behaviour with refusing every task | Our experiment is source-text review, not AgentDojo reproduction |
| TrojanPuzzle, https://arxiv.org/abs/2301.02344 | Training-data poisoning of code suggestion | Separate model compromise from inference evasion | No poisoned LLM trained here |
| BaxBench, https://arxiv.org/abs/2502.11844 and https://github.com/logic-star-ai/baxbench | Generated-code correctness versus security | Security labels differ from functional test success | No BaxBench benchmark run |
| SeRe, https://arxiv.org/abs/2601.01042 | Security-related code review corpus | Real review data is a future external-validation step | Preprint reading lead, not reused data |
| Semgrep official taint docs, https://docs.semgrep.dev/writing-rules/data-flow/taint-mode/overview | Source/sink propagation and edition-dependent capabilities | Pin Community Edition and local taint rules | Single-function parameter source assumptions are narrow |
| MLX-LM, https://github.com/ml-explore/mlx-lm | Local Apple Silicon inference | Real model calls with tokens, latency, raw outputs | Quantised small model limits conclusions |
| Qwen model card, https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct | Code instruction model | Use chat template and explicit structured task | Chosen for local budget, not capability leadership |
| MLX community artifact, https://huggingface.co/mlx-community/Qwen2.5-Coder-1.5B-Instruct-4bit | Converted 4-bit artifact | Pin revision and verify hashes | Conversion adds a supply-chain dependency |
| QUB Candidate Information, https://hr.apps.qub.ac.uk/jobs/job_desc/26_113642.pdf | Eight RA duties | Link each duty to actual artifacts and limits | A pilot cannot substitute for industry collaboration or peer review |

## Gap tested
A small oracle-assisted adaptive audit can estimate a frozen reviewer's correctness profile. The experiment asks whether an A-IPES-inspired acquisition adds value over fixed coverage and random testing. It separately tests whether a static-check union improves review recall at tolerable false-alarm and latency cost. Neither question presupposes a positive result.
