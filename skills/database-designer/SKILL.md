---
name: database-designer
description: "Design application data models, schemas, constraints, indexes, transactions, queries, and safe migrations from explicit workloads. Use when a service needs durable data structure, query-path review, relational or document modeling, or a rollback-aware schema evolution plan."
---

# Database Designer
Shape application data so invariants hold and dominant queries remain predictable at expected scale.

## Workflow
1. Inspect domain contracts, current schema, representative data, query paths, and deployment constraints.
2. Define entities, identities, relationships, cardinalities, ownership, retention, and lifecycle.
3. Encode required invariants with types, constraints, keys, and transaction boundaries.
4. Normalize by default, then justify denormalization from measured or modeled access patterns.
5. Design indexes from concrete predicates, joins, ordering, selectivity, and write cost.
6. Model concurrency, isolation, retries, locking, and failure during multi-step changes.
7. Plan expand-migrate-contract stages, backfill verification, rollback, and compatibility tests.

## Decision Boundaries
- Use the storage-engine specialist for WAL, buffer managers, compaction, or engine internals.
- Do not apply migrations, inspect production data, or change external databases without approval.
- Do not invent cardinality, retention, latency, consistency, or compliance requirements.
- Avoid choosing a database product when the task only requires a logical model.
- Coordinate public schema changes with API and contract compatibility requirements.

## Quality Gates
- Specify nullability, uniqueness, referential actions, defaults, and deletion semantics.
- Test empty, duplicate, orphaned, maximum-size, and concurrent-write cases.
- Explain query and index complexity plus storage and write amplification tradeoffs.
- Preserve old and new application compatibility during staged migrations.
- Require reconciliation evidence before destructive contraction.

## Output Contract
- Provide the logical model, key invariants, and relationship cardinalities.
- List physical schema choices and the workload evidence supporting each index.
- Define transaction and isolation boundaries with expected conflicts.
- Present migration, backfill, verification, and rollback steps.
- Mark assumptions, unavailable data evidence, and unexecuted query plans.
