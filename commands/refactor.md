---
description: Plan or execute a behavior-preserving structural refactor in a bounded scope.
argument-hint: target paths, structural objective, invariants, and apply or plan intent
---

# Guide Refactor

Preserve all text following `/refactor` as task input. When empty, use the active
target and ask for the structural objective.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/refactoring-guide/SKILL.md`.
2. Inspect callers, contracts, tests, side effects, dependencies, and observable
   behavior before proposing transformations.
3. Follow the skill's staged workflow, decision boundaries, quality gates, and
   output contract.
4. Default to a read-only plan; edit only when the input explicitly requests
   applying the refactor.

Report preserved invariants, ordered transformations, validation, rollback
points, and remaining coupling concisely. Never mix unrelated features or claim
behavior preservation without executed checks.
