# Understand and demonstrate CodeGuard

## The simple story

Imagine hiring a code inspector. You can afford only a few checks. Your dissertation asks which experiment tells you most about an agent's rules. CodeGuard asks which labelled code example tells you most about a reviewer's reliability. They share a testing philosophy, but their hidden objects differ: a finite runtime policy in A-IPES, an estimated correctness probability in CodeGuard.

The experiment changes the presentation of a short program while preserving its intended security-relevant behaviour under stated assumptions. Renaming a variable should not make unsafe SQL safe. Yet the model sometimes changes its verdict. We measure those changes, then compare a simple scanner and a union rule. The scanner catches the toy vulnerabilities but also flags one safe path family. That is the real result; it does not prove all scanners beat all language models.

## What you must be able to explain without notes

1. Ground truth comes from manually designed vulnerable/safe pairs and explicit assumptions, not from Semgrep's output. Labels are single-author judgements; independent audit is needed.
2. Three vulnerability families are SQL injection, shell command injection and path traversal. The corpus is text, never executed.
3. Four representations are original, local variable rename, AST formatting and helper wrapper. Formatter equality and inverse rename checks are structural evidence; no claim of general semantic-equivalence proof.
4. A source review component receives code plus a frozen prompt. No tools, repository permissions or autonomous actions are involved.
5. Safe and vulnerable siblings stay in one base family. Families 0-2 are development; 3-5 are test within each weakness. Related variants are not independent samples.
6. Each of 12 class/representation cells has Beta(1,1) prior. Correct review increments alpha, incorrect review increments beta. Predicted correctness is alpha/(alpha+beta).
7. A selected probe needs known truth to reveal correctness. This is oracle-assisted offline evaluation. In deployment an expert or validated oracle would have to pay that labelling cost.
8. Expected information measures anticipated uncertainty reduction, not vulnerability severity. The policy term asks whether reliability is below a chosen 0.8 threshold; 0.8 is an experimental parameter, not a safety standard.
9. The full score is normalised outcome information + 1.5 policy information + 0.2 boundary + 0.1 novelty. This adapts dissertation components; it is not the original finite-policy algorithm.
10. Brier score averages (predicted correctness - actual correctness)^2 over held-out samples. Lower is better. Predicting 0.5 for everyone gives exactly 0.25 here. The full method's 0.2679 at B24 is worse even than that reference. The protocol did not designate the 0.5 reference as primary; include it as an explanatory baseline.
11. A policy-threshold objective and a probability-estimation endpoint need not agree. This is a plausible explanation for the failed transfer, not an experimentally isolated cause. Correlation, small data and development/test differences also matter.
12. 100 seeds vary probe choice; they do not create 100 independent models. Nine held-out family clusters determine the exploratory uncertainty calculation.
13. A union defence flags a class when either reviewer flags it. It cannot lower false positives relative to either component on valid paired cases. It should never silently erase scanner findings.
14. All results are conditional on one small community-quantised model, a fixed prompt and toy code. Do not call it a general evaluation of Qwen or autonomous agents.
15. Hash verification is provenance-related integrity practice. An unsigned hash list is not cryptographic attestation of a trusted build or proof of authorship.

## Two-minute recorded demonstration

From the repository root, run `python -m codeguard.demo` after installing the documented environment. It needs no model download. Say at the start: 'This replays recorded real-model outputs, so the demonstration is reproducible and does not depend on live inference.'

0:00-0:25: Show original SQL example and its ground-truth assumption. Explain that a parameter value is concatenated into query structure. Do not execute the source.

0:25-0:50: Show the renamed example. The structural inverse-rename check passes; the local model changes from detected to missed. Explain that this illustrative example was selected after the evaluation and is not an independent new result.

0:50-1:15: Show Semgrep and union flags. State that the scanner remains positive and the union retains that finding.

1:15-1:40: Show aggregate counts: 10/36 to 36/36 detections, but 0/36 to 4/36 safe flags. State that Semgrep alone already achieves the hybrid result.

1:40-2:00: Explain why adaptive selection did not improve the main metric, and name the next independently planned test: broader families, stronger second model, independent labels, then a fresh frozen holdout.

## Interview questions to practise

**Is this still one piece of work?** 'I present A-IPES as one research line, with CodeGuard as a clearly separated post-dissertation transfer experiment.' Keep dissertation results and new pilot results labelled.

**What did you personally do?** Describe only work you have actually reviewed, reproduced, modified and understood. This extension was built with AI assistance. Do not imply you wrote all generated code unaided or ran experiments before they were actually run. Explain your decisions and verification precisely.

**Why did the adaptive approach fail?** 'Its threshold-oriented acquisition did not improve held-out probability prediction here. Removing policy information reduced Brier at B24, but that ablation does not by itself establish a universal cause. I would test objective alignment on a fresh protocol.'

**Why not just use Semgrep?** 'On this corpus, I would. The hybrid has no measured incremental value over Semgrep, so its extra model cost is unjustified for this benchmark. The next question is where their errors are complementary on realistic code.'

**Why is zero observed FPR not proof of safety?** 'There are only 36 held-out safe variants, grouped into nine families. Unseen safe code can still trigger false alarms, and the model misses many vulnerabilities.'

**Have you investigated poisoned models?** 'I studied the mechanism and built a labelled toy trigger demonstration. I have not poisoned or evaluated a backdoored LLM.'

**What is novel?** 'This pilot is a transfer investigation and reproducible evaluation artifact. Novelty against prior work is not established; I would conduct broader reconnaissance before claiming a publishable contribution.'

**What would you change first?** 'Independent label review and a structurally broader corpus; then a stronger second model, repeated timing and a predeclared objective that matches the acquisition function.'

## Preparation schedule to the confirmed deadline

10 October: read the code and report; reproduce tests and cached demo; explain every metric aloud. Write down any statement you cannot yet defend.

11 October: rehearse an eight-minute dissertation-plus-extension talk; practise the eight questions above; reproduce one selector trace by hand. Have a mock interviewer challenge the weak results and ownership claims.

12 October: run two timed mocks; check every slide number against recorded evidence; verify the deck on the actual presentation software; export/inspect a backup PDF. Aim to finish the submission copy today.

13 October: submit before 09:00 UK using the required job reference, after checking the attachment opens. Sending is the candidate's responsibility; nothing has been emailed automatically.

14 October: practise concise answers and one whiteboard architecture. Avoid changing the experimental story after submission; prepare clarifications as backup notes.

15 October: present the central question, evidence and limitations calmly. There is no guaranteed interview outcome; credibility rests on your understanding and truthful answers.
