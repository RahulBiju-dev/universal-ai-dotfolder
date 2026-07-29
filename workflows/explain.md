---
name: explain
description: Explain concrete code through control flow, state, ownership, and contracts.
---

# Code Explanation Trajectory

When `/explain` is invoked, preserve all trailing text as task input; otherwise
resolve the active selection or request a code target.

1. Read `../skills/code-explainer/SKILL.md`.
2. Inspect definitions, callers, state, data flow, ownership, errors, tests, and
   relevant platform semantics.
3. Build a layered explanation calibrated to the requested learning goal.
4. Keep the trajectory read-only and separate explanation from code review.
5. Return path-grounded behavior, invariants, complexity, and inferred intent
   concisely without claiming unobserved runtime facts.
