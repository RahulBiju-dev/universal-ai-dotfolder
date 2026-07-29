---
description: Locate the first regression revision using a deterministic predicate safely.
argument-hint: known-good revision, known-bad revision, predicate command, and constraints
---

# Bisect Regression

Preserve all text following `/bisect` as task input. When empty, require
known-good and known-bad boundaries plus a reproducible predicate.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/regression-bisector/SKILL.md`.
2. Inspect repository state, history topology, predicate determinism, build
   prerequisites, submodules, generated state, and flaky behavior.
3. Follow the skill's safe traversal, classification, decision boundaries,
   quality gates, and output contract.
4. Default to a read-only bisect plan; execute only when explicitly requested
   and isolation preserves the user's working tree.

Report tested revisions, predicate outcomes, skipped states, first bad change,
and confidence concisely. Never rewrite history or claim causation from an
unverified boundary.
