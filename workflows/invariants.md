---
name: invariants
description: Derive and falsify candidate contracts from code, tests, and traces.
---

# Invariant-Mining Trajectory

When `/invariants` is invoked, preserve all trailing text as task input;
otherwise use the active target and intended invariant use.

1. Read `../skills/invariant-miner/SKILL.md`.
2. Inspect contracts, types, branches, loops, state, ownership, concurrency,
   tests, specifications, and traces.
3. Generate candidates, search for counterexamples, and assign evidence-based
   confidence.
4. Keep mining read-only unless assertions or tests are explicitly requested.
5. Return each invariant's scope, source, confidence, counterexamples, and
   verification strategy concisely.
