---
description: Design or critique a distributed system through explicit failures and guarantees.
argument-hint: services, state, workload, consistency, failures, and scale constraints
---

# Design Distributed System

Preserve all text following `/distributed` as task input. When empty, use the
active distributed design question.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/distributed-systems-design/SKILL.md`.
2. Inspect state ownership, messages, retries, ordering, clocks, partitions,
   replication, idempotency, capacity, recovery, and observability.
3. Follow the skill's failure-model reasoning, decision boundaries, quality
   gates, and output contract.
4. Keep critique and design read-only unless implementation is explicitly
   requested.

Report guarantees, assumptions, failure behavior, scaling limits, alternatives,
and validation needs concisely. Never claim exactly-once, consistency, or
availability beyond the stated model and evidence.
