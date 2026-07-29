---
name: migrate
description: Produce a staged migration with coexistence, reconciliation, and rollback.
---

# Migration Trajectory

When `/migrate` is invoked, preserve all trailing text as task input; otherwise
request source and target states.

1. Read `../skills/migration-planner/SKILL.md`.
2. Inspect readers, writers, data, contracts, jobs, caches, deployment order,
   scale, and recovery constraints.
3. Define expand, migrate, verify, cutover, contract, and cleanup gates.
4. Keep the trajectory read-only; never alter data, run migrations, or deploy.
5. Return phases, backfill, observability, rollback, irreversible points, and
   assumptions concisely.
