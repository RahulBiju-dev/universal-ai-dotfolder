---
name: distributed
description: Design distributed behavior from explicit failure and consistency models.
---

# Distributed-System Trajectory

When `/distributed` is invoked, preserve all trailing text as task input;
otherwise use the active system-design question.

1. Read `../skills/distributed-systems-design/SKILL.md`.
2. Inspect state ownership, messages, retries, clocks, partitions, replication,
   idempotency, capacity, recovery, and observability.
3. Derive guarantees and degradation behavior from an explicit failure model.
4. Keep design and critique read-only unless implementation is requested.
5. Return assumptions, guarantees, alternatives, scaling limits, and validation
   needs concisely without overclaiming consistency or availability.
