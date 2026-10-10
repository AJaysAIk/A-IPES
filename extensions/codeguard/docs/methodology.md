# Evaluation contract

## Reviewer extension

Implement `name`, `version`, and `review(ReviewInput) -> ReviewResult` to satisfy `CodeReviewer`; pass the instance to `evaluate(samples, reviewer)`. Adapters must map provider outputs to supported class names and positive, one-based source lines. They must raise on unavailable providers, refusals, malformed responses, or incomplete reviews; an empty findings list is reserved for a successfully completed negative review.

Future adapters should record model revision, prompt hash, generation settings, and retry policy in an expanded report schema. Do not put API keys or private source in results. The current report records a detector version, not full future model provenance.

## Ground truth and scoring

`load_corpus` defines the manifest and expected labels explicitly. Source order produces opaque sample IDs, independent of the filename labels sent to the evaluator. Reviewers receive no paths or expected labels, although the handcrafted source is not a blinded benchmark. Samples and labels contribute to the corpus fingerprint.

Each of six samples has three class decisions. A SQL fixture with a command-injection prediction incurs one SQL false negative and one command-injection false positive. Multiple identical findings do not increase counts. Safe fixtures have three negative decisions each. Corpus-level metrics pool all 18 decisions; per-class reports have six decisions each.

Precision = TP/(TP+FP); recall = TP/(TP+FN); F1 = 2TP/(2TP+FP+FN); accuracy = (TP+TN)/N. A zero denominator yields zero. Empty corpora are rejected.

## Threat model and research scope

Inputs are source text provided for authorized review. The labelled weaknesses concern untrusted values reaching SQL syntax, shell interpretation, or a file path. No attack strings or real services are needed. The evaluation process does not import sample modules. Semgrep scans temporary copies and is subject to a 120-second process timeout; its errors and scanned-file inventory are checked before scoring.

A malicious or buggy reviewer could still produce plausible but incorrect findings. Schema validation checks structure, not truth. Ground-truth comparisons expose errors only within this small corpus. A clean run says nothing about unknown weaknesses.

## Toward publishable evaluation

Before making comparative research claims, define research questions and a held-out corpus, separate rule/prompt development from testing, document annotation disagreements, choose meaningful baselines, and repeat stochastic inference. Report paired differences with uncertainty, failure and abstention rates, and qualitative error cases. Keep results tied to exact source, rules, model and prompt revisions. This scaffold supplies the mechanics; those experiments remain future work.
