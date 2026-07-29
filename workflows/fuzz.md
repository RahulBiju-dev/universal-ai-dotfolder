---
name: fuzz
description: Define a bounded fuzz harness, corpus, oracle, and crash-triage loop.
---

# Fuzzing Trajectory

When `/fuzz` is invoked, preserve all trailing text as task input; otherwise use
the active hostile-input boundary.

1. Read `../skills/fuzzing-strategy/SKILL.md`.
2. Inspect parsers, invariants, harnesses, corpora, formats, sanitizers, side
   effects, determinism, and crash handling.
3. Specify target, oracle, generators, dictionary, budget, and minimization.
4. Default to read-only strategy; create or execute fuzzing only when explicit.
5. Return the campaign plan, resource bounds, triage, and measured coverage
   evidence concisely without claiming unrun safety.
