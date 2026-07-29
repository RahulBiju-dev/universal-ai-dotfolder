---
description: Mine candidate behavioral and ownership invariants from code, tests, and traces.
argument-hint: target symbol or subsystem, evidence sources, and intended use
---

# Mine Invariants

Preserve all text following `/invariants` as task input. When empty, use the
active target and ask whether the result supports tests, assertions, or refactoring.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/invariant-miner/SKILL.md`.
2. Inspect contracts, types, branches, loops, state transitions, ownership,
   concurrency, tests, specifications, and available traces.
3. Follow the skill's candidate classification, falsification, decision
   boundaries, quality gates, and output contract.
4. Keep mining read-only unless assertions or tests are explicitly requested.

Return candidate invariants with source, scope, confidence, counterexamples, and
verification strategy concisely. Never promote an observed pattern to a
guarantee without proof.
