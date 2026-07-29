---
name: migration-planner
description: Design staged, reversible migrations for databases, schemas, APIs, protocols, file formats, configuration, runtimes, services, or repositories. Use when old and new states must coexist, data requires backfill, consumers need sequencing, or rollout and rollback safety must be explicit.
---

# Migration Planner

Convert a target-state change into observable phases that preserve service and data integrity.

## Workflow

1. Define source state, target state, invariants, owners, consumers, scale, and success criteria.
2. Inventory readers, writers, stored data, contracts, jobs, caches, tooling, and deployment order.
3. Identify compatibility gaps and the earliest irreversible transition.
4. Design expand, migrate, verify, cut over, and contract phases.
5. Specify idempotent backfills, checkpoints, throttling, retries, quarantine, and reconciliation.
6. Define mixed-version behavior, pause conditions, rollback, and disaster recovery.
7. Assign entry gates, exit gates, telemetry, and ownership to every phase.

## Decision Boundaries

- Keep planning and diagnosis read-only unless execution is explicitly requested.
- Never run migrations, alter data, deploy, or mutate external systems without approval.
- Prefer dual-read or dual-write only when consistency and rollback semantics are defined.
- Reject flag-day transitions when staged compatibility is feasible.
- Use repository search or architecture mapping only to resolve concrete dependency uncertainty.

## Quality Gates

- Preserve authoritative data and identify the source of truth in every phase.
- Make each step restartable or document why it cannot be.
- Quantify volume, duration, load, storage, and failure assumptions.
- Define reconciliation evidence before deleting old paths or formats.
- Never claim migration safety without tested representative transitions.

## Output Contract

- Return a phase table with actions, owners, entry gates, exit gates, and observability.
- Document compatibility states, backfill mechanics, cutover, rollback, and cleanup.
- Separate verified repository facts from operational assumptions.
- State irreversible points, open decisions, and validation still required.
