---
name: edge-cases
description: Enumerate reachable boundary and failure cases with regression priorities.
---

# Edge-Case Trajectory

When `/edge-cases` is invoked, preserve all trailing text as task input;
otherwise use the active file or diff.

1. Read `../skills/edge-case-hunter/SKILL.md`.
2. Inspect contracts, callers, validation, cleanup, tests, limits, partial
   operations, and relevant interleavings.
3. Rank only reachable cases by impact, likelihood, and current coverage.
4. Keep analysis read-only unless fixes or tests are explicitly requested.
5. Return triggers, expected safe behavior, evidence, and coverage concisely;
   never claim unrun handling.
