---
name: bisect
description: Narrow a regression to the first bad revision with a deterministic predicate.
---

# Regression-Bisect Trajectory

When `/bisect` is invoked, preserve all trailing text as task input; otherwise
require known-good, known-bad, and predicate inputs.

1. Read `../skills/regression-bisector/SKILL.md`.
2. Inspect working-tree state, history topology, predicate determinism, build
   prerequisites, submodules, generated state, and flakiness.
3. Plan or execute safe isolated revision classification in deterministic order.
4. Never rewrite history or disturb user changes; execute only when explicitly
   requested.
5. Return tested revisions, outcomes, skips, boundary, and confidence concisely
   without overstating causation.
