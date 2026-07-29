---
name: refactor
description: Stage a behavior-preserving refactor with explicit invariants and rollback.
---

# Refactoring Trajectory

When `/refactor` is invoked, preserve all trailing text as task input; otherwise
request the structural objective for the active target.

1. Read `../skills/refactoring-guide/SKILL.md`.
2. Inspect callers, contracts, tests, side effects, dependencies, and observable
   behavior.
3. Order small reversible transformations and establish characterization gates.
4. Default to read-only planning; edit only when applying the refactor is
   explicit.
5. Return preserved invariants, steps, checks, rollback points, and remaining
   coupling concisely without mixing feature work.
