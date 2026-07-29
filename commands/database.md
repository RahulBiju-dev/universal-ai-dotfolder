---
description: Design a workload-driven data model, query path, transaction, and migration plan.
argument-hint: entities, workloads, scale, consistency, retention, and existing schema
---

# Design Database

Preserve all text following `/database` as task input. When empty, use the active
data-model problem and ask for missing workloads.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/database-designer/SKILL.md`.
2. Inspect current schemas, queries, constraints, indexes, transactions,
   cardinality, retention, migrations, and failure behavior.
3. Follow the skill's workload modeling, decision boundaries, quality gates,
   and output contract.
4. Keep design read-only unless schema or code changes are explicitly requested;
   never execute a migration here.

Report the model, constraints, query/index rationale, transaction semantics, and
migration risks concisely. Separate measured workload facts from estimates and
never assert performance without validation.
