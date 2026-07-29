---
description: Review concurrent code for races, deadlocks, cancellation, and lifecycle defects.
argument-hint: concurrent target, symptom, synchronization model, and workload
---

# Review Concurrency

Preserve all text following `/race` as task input. When empty, use the active
concurrent code or timing-dependent failure.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/concurrency-review/SKILL.md`.
2. Inspect shared state, publication, lock ordering, atomics, queues, task
   ownership, cancellation, shutdown, and blocking operations.
3. Follow the skill's interleaving analysis, decision boundaries, quality gates,
   and output contract.
4. Keep review read-only unless fixes are explicitly requested; ask before
   stress or race-detector execution.

Report severity-ranked interleavings, evidence, violated invariants, and the
minimal verification strategy concisely. Separate code-proven defects from
plausible schedules and never fabricate race-detector output.
