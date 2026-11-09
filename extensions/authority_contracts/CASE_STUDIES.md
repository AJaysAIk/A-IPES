# Three concrete counterexamples from the development pilot

These are observed planted-fault witnesses, not failures in ATC or live agents.
The healthy-control comparison below is an additional illustrative replay.

## stale_revision

First observed violation at executed action 377 of the 1,000-action cap (seed 0).

| Step | Public action | Faulty response | Correct-control response | Fault monitor violation |
|---|---|---|---|---|
| 1 | verify | ok | ok | False |
| 2 | approve | ok | ok | False |
| 3 | edit | ok | ok | False |
| 4 | execute | committed | denied | True |

## expired_approval

First observed violation at executed action 447 of the 1,000-action cap (seed 0).

| Step | Public action | Faulty response | Correct-control response | Fault monitor violation |
|---|---|---|---|---|
| 1 | verify | ok | ok | False |
| 2 | approve | ok | ok | False |
| 3 | verify | ok | ok | False |
| 4 | verify | ok | ok | False |
| 5 | verify | ok | ok | False |
| 6 | execute | committed | denied | True |

## role_bypass

First observed violation at executed action 221 of the 1,000-action cap (seed 0).

| Step | Public action | Faulty response | Correct-control response | Fault monitor violation |
|---|---|---|---|---|
| 1 | verify | ok | ok | False |
| 2 | approve | ok | ok | False |
| 3 | reviewer_execute | committed | denied | True |

## What these witnesses establish

Each trace demonstrates a concrete violation of the stated operational contract
by one deliberately faulty development implementation. The healthy control refuses
the problematic commit. These traces do not establish completeness of the tester,
coverage of other faults, natural-language contract understanding, or general safety.
