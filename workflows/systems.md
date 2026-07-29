---
name: systems
description: Route low-level code through ownership, bounds, syscall, and cleanup discipline.
---

# Systems Trajectory

When `/systems` is invoked, preserve all trailing text as task input; otherwise
use the active low-level target.

1. Read `../skills/systems-programming/SKILL.md`.
2. Inspect ABI and platform contracts, ownership, arithmetic, syscalls, partial
   I/O, concurrency, cleanup, tests, and complexity.
3. Apply the skill's safety and implementation gates to the requested scope.
4. Mutate code only when implementation is explicit; require approval for
   privileged or hardware-facing execution.
5. Return ownership, failure behavior, complexity, changes, and validation
   evidence concisely without inventing runtime results.
