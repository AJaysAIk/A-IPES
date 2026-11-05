# A-IPES-V preliminary pilot findings

## What was tested

The initial pilot compared specification-aware A-IPES-V against the original policy-active A-IPES selector and seeded random probing on a controlled five-tool benchmark.

The monitored specifications were:
1. supplier approval requires verified evidence;
2. purchase authorisation requires prior supplier approval;
3. publication requires verified evidence;
4. resource calls must not exceed five.

## Preliminary result

On the first validated pilot run, A-IPES-V and the original policy-active selector selected the same safety-relevant first probes for the four unsafe tools and both detected the available violation at probe 1. Random probing was weaker at budget 1 in that seed.

This is **not evidence that A-IPES-V improves over A-IPES**.

The likely reason is structural redundancy: the original A-IPES policy-information term already encodes essentially the same four unsafe transition conditions used by this first specification set. Adding an explicit specification-information term therefore does not create a distinct acquisition objective in this benchmark.

## Why this matters

The null result is useful because it identifies the next experimental requirement. A meaningful test of specification-aware acquisition must include safety properties that are not already reducible to the existing policy-unsafe predicate.

The next benchmark revision should therefore introduce:
- non-redundant specifications;
- state-dependent safety requirements not represented by the original binary policy label;
- temporal or multi-step constraints;
- counterexample-oriented evaluation;
- matched computational budgets and paired seeds.

## Research claim boundary

At this stage the extension demonstrates an implementation of specification-aware scoring and runtime monitors, plus a negative result on a redundant specification set.

It does not yet demonstrate an advantage over original A-IPES, formal verification, model checking, temporal-logic guarantees, or deployed-agent safety.
