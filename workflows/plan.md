---
name: plan
description: Produce an ordered implementation plan with dependencies, gates, and rollback.
---

# Planning Trajectory

When `/plan` is invoked, preserve all trailing text as task input; otherwise use
the accepted objective in the current conversation.

1. Read `../skills/task-planner/SKILL.md`.
2. Inspect affected code, interfaces, tests, dependencies, and repository
   constraints.
3. Decompose work into atomic dependency-aware steps with acceptance gates.
4. Keep the trajectory read-only and include rollback and stop conditions.
5. Return the plan, assumptions, risks, and unverified feasibility evidence
   concisely.
