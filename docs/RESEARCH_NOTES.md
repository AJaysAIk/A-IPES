# Research notes and limitations

The main evidence is a controlled synthetic Benchmark V2 study over 30 generated worlds, paired across strategies. It does not establish performance on live MCP deployments, proprietary coding agents, real LLM decision policies, or arbitrary unseen policy families.

The simulator exposes exact state-transition labels and uses a finite hypothesis library. Metadata priors differ between passive characterisation and active selection; the comparison therefore should not be interpreted as a matched-prior causal isolation of acquisition alone. A single probe seed is used for the primary experiment, distinct from the 30 benchmark seeds. Report paired world-level analyses, not individual trajectories as independent experimental replicates.

A-IPES does not dominate at every budget. At budget 2, passive characterisation has better recall and policy exact match. At budget 5, adaptive selection improves these metrics in the recorded evaluation. Zero observed false positives is limited to these evaluated worlds and scenarios.

Component ablation tests remove acquisition terms. Interpret those findings within this hypothesis family and benchmark; they are not universal rankings of acquisition strategies. External systems mentioned in historical literature notes are motivation, not reproduced implementations or head-to-head evaluations.

The published CSVs are archived dissertation outputs, not newly generated measurements from the publication preparation. Local validation is recorded separately in VALIDATION.md. Historical protocol documents can describe earlier experiments or proposed extensions.

For exact reproduction, keep the full budget list `1,2,3,5`: random probe orderings are drawn using the maximum requested budget, so a smaller budget list can change the random baseline even with the same seed.
