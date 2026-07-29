---
description: Design a staged, compatible, and rollback-aware technical migration.
argument-hint: source state, target state, consumers, data volume, and constraints
---

# Plan Migration

Preserve all text following `/migrate` as task input. When empty, use the active
migration proposal and request its source and target states.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/migration-planner/SKILL.md`.
2. Inspect readers, writers, data, contracts, jobs, caches, deployment order,
   compatibility states, and recovery constraints.
3. Follow the skill's phased planning, decision boundaries, quality gates, and
   output contract.
4. Keep this route read-only; never run migrations, mutate data, or deploy.

Return phases, entry and exit gates, backfill mechanics, observability,
cutover, rollback, and irreversible points concisely. Separate repository facts
from operational assumptions.
