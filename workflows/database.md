---
name: database
description: Design workload-driven schemas, constraints, indexes, and safe evolution.
---

# Database Trajectory

When `/database` is invoked, preserve all trailing text as task input; otherwise
request the data model and workloads.

1. Read `../skills/database-designer/SKILL.md`.
2. Inspect schemas, queries, cardinality, constraints, indexes, transactions,
   retention, failure behavior, and migration history.
3. Select a model from explicit read and write workloads.
4. Keep design read-only unless schema edits are requested; never execute a
   migration in this trajectory.
5. Return the model, query rationale, transaction semantics, evolution plan, and
   evidence limits concisely.
