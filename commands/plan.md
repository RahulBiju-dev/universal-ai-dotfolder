---
description: Convert an accepted objective into a dependency-aware implementation plan.
argument-hint: objective, target paths, constraints, and acceptance criteria
---

# Plan Work

Preserve all text following `/plan` as task input. When empty, use the accepted
objective in the current conversation.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/task-planner/SKILL.md`.
2. Inspect affected code, interfaces, tests, dependencies, and repository
   constraints before ordering work.
3. Follow the skill contract to define atomic steps, gates, rollback points,
   risks, and validation.
4. Keep planning read-only; do not edit or execute the plan in this route.

Return a concise ordered plan grounded in inspected evidence. Label assumptions
and unresolved dependencies, and never claim feasibility or validation that was
not established.
