---
name: race
description: Trace concurrent interleavings for races, deadlocks, and lifecycle failures.
---

# Concurrency-Review Trajectory

When `/race` is invoked, preserve all trailing text as task input; otherwise use
the active concurrent target or intermittent symptom.

1. Read `../skills/concurrency-review/SKILL.md`.
2. Inspect shared state, publication, lock ordering, atomics, queues,
   cancellation, shutdown, and blocking work.
3. Construct only reachable interleavings and identify violated invariants.
4. Keep review read-only unless fixes are requested; ask before dynamic stress
   or race detection.
5. Return severity, schedule, evidence, consequence, and verification strategy
   concisely without fabricating tool output.
