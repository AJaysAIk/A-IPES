# Jha-aligned evidence sprint: feasibility protocol

6 November 2026. This document is fixed before executing this pilot. It is an
engineering feasibility check on development fixtures, not held-out research
validation or a comparison establishing a winner.

Question: can an established automata learner with black-box checking be connected
to an independently implemented stateful tool, with an external contract monitor
and exact accounting of all real action calls?

The adapter is a local SQLite document-approval service. Actions: verify evidence,
reviewer approve, edit document, revoke approval, executor commit, reviewer commit,
and idle. A successful commit requires the executor role, evidence and approval
bound to the current document, no revocation, and approval age <=3. Every action
advances a logical clock; approval resets its age to zero. Refusal is permitted.
The monitor uses public input/output history, not the database's internal state.

Four development fixtures: correct control; ignore revision/evidence freshness;
ignore approval expiration; allow reviewer commits. The faults are intentionally
injected. No live agent or real MCP server is evaluated.

AALpy 2.0.0 L* Mealy learner with RandomWMethodEqOracle (walks_per_state=10,
walk_len=6), wrapped in the library's BBCEqOracle. Its property oracle searches
the learned-model/contract-monitor product breadth-first to depth six. A predicted
counterexample is replayed on the actual service by the library. The property
oracle inspects only model predictions; no service state is used for selection.
Every service call, including learner and oracle calls, is externally monitored.
Cache hits do not execute the service and incur zero actual-action cost.

Compare wiring with a seeded uniform random-input tester using six-action reset
traces. Seeds 0,1,2, cap 1,000 executed actions per fixture/strategy. Reset count is
separate. If learning terminates early, fill the remaining budget with the same
random-trace procedure and label the strategy Lstar_BBC_then_random. If the cap
interrupts a learner/oracle query, retain its observed prefix and report budget
exhaustion without a convergence claim. No incomplete query becomes a label.

Save every executed action, output, query prefix, monitor verdict, executed-call
index and reset count, plus summary rows and source hashes. Tests must exercise
safe controls, distinct planted faults, monitor independence, exact budgets,
property-oracle search and reproducibility. Check independently known witnesses
in tests; those are not supplied to the learner or treated as evaluation results.

Go condition: functioning adapter, standard learner and BBC validation loop,
correct accounting and reproducible evidence. Success is feasibility, not research
novelty. Failure is reported and fixed without claiming a scientific advantage.
A subsequent study requires a new frozen protocol, independent implementations,
held-out faults and a documented conformance-testing baseline. No additional
acquisition method or experiment tuning is authorised by a favourable pilot.
