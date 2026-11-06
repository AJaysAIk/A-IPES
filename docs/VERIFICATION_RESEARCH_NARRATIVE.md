# A-IPES-V: evidence-led dissertation narrative draft

This is a working narrative for the verification extension, not a replacement for
the original dissertation or a publication-ready literature/novelty claim. The
v0.1–v0.3 statements below summarize existing repository findings; v0.4–v0.6 link
to their recorded evidence. Development, held-out context transfer, and temporal
adaptations must be described as different evaluations.

## Research question and progression

The extension asks whether intervention selection should explicitly account for
a known safety specification when the aim is to discover concrete violations.
Its contribution should be framed as an implemented acquisition-and-monitoring
study with controlled comparisons and documented failure cases. The experiments
do not establish a generally superior verification algorithm.

The initial pilot found no incremental benefit when the runtime specifications
repeated conditions already represented by the original A-IPES policy-unsafe
predicate. This motivated a development benchmark with contextual resource
requirements outside that predicate. In v0.2, specification-active probing found
20/20 unsafe world-seed cases at the first probe, compared with 0/20 for original
policy-active A-IPES. Because that benchmark was constructed to isolate the new
objective after the initial null result, it is development evidence rather than
an unbiased generalization test.

v0.3 showed that this development result depended on acquisition weighting:
specification weights 0.5 and 1.0 failed at budget 1, while weight 2.0 succeeded
without an expected-violation term. The chosen setting was then fixed for v0.4.
Across four new contextual predicates, first-probe detection was 60/80, increasing
to 80/80 by the second probe. The first-probe failures were all in the conjunction
context. This supports limited transfer within the contextual-resource template,
not transfer to arbitrary specifications or tool dynamics.

The temporal adapter in v0.5 changed both the task and comparator: it queried
four-action histories and compared specification-weighted acquisition with
response entropy, finite-model CEG, and random probing. The temporal
response-entropy comparator is not the unchanged original policy-active A-IPES.
Specification and response-only methods both detected 80/120 unsafe cases after
one trace and 120/120 after two; CEG detected 84/120 then 120/120. The absence of
incremental value from specification weighting is a central result to retain.

v0.6 kept the small hypothesis library but introduced lease expiry and six-action
traces. It separated observed specification violations from model inadequacy,
which was recorded only when no hypothesis matched all observations. At eight
traces, the information methods each detected 90/160 unsafe cases and flagged
92/200 out-of-class cases. CEG detected 122/160 and flagged 178/200 respectively.
All methods missed some out-of-class cases within the fixed budget. Model
consistency therefore cannot be used as a sufficient condition for adequacy.

## Interpretation for discussion

Three distinctions organize the findings. First, a specification term helps only
when it changes useful intervention priorities; adding it does not inherently
improve discovery. Second, property violations and model mismatch are different:
a safely expiring tool can refute the model library, while an in-class tool can
still violate the lease specification. Third, a strong counterexample-guided
baseline is essential. Its competitive or better performance prevents attributing
all successful discovery to the proposed acquisition rule.

The strongest defensible conclusion is conditional: explicit specification
information can improve early discovery on selected non-redundant contextual
worlds, but that benefit did not persist as an incremental advantage over response
entropy in the two bounded temporal experiments. The mismatch experiment exposes
a further limitation: discovery-oriented acquisition can leave an inadequate
model unrefuted, and after collapse the current method has no model-repair policy.

## Validity limits to retain in the dissertation

All environments are synthetic and deterministic. Repeated seeds change ordering
rather than sampling independent tools. The search pools are finite; exhaustive
labels refer only to those pools. Resets are free in the action-call budget.
Weights were chosen from development results. Later protocols freeze choices but
do not turn the entire research sequence into a prospective study. There are no
real-agent traces, unbounded proofs, deployment guarantees, or population-level
statistical generalization results. Logical search-work counters are not CPU-time
comparisons. A formal novelty claim would require a separate literature review.

## Evidence map and next experiment

- [Initial null pilot](../extensions/aipes_v/PILOT_FINDINGS.md)
- [Development result](../extensions/aipes_v/V02_RESULTS.md)
- [Weight sensitivity](../extensions/aipes_v/V03_RESULTS.md)
- [Held-out contextual transfer](../extensions/aipes_v/V04_RESULTS.md)
- [Realizable temporal evaluation](../extensions/aipes_v/V05_RESULTS.md)
- [Temporal misspecification evaluation](../extensions/aipes_v/V06_RESULTS.md)

A next protocol could compare model expansion after posterior collapse with the
current uniform exploration fallback. Lease-clock expansion should incur explicit
search and action-call costs, and must be evaluated on additional withheld
behaviours. This is future work, not an outcome of the current study.
