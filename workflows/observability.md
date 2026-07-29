---
name: observability
description: Derive bounded telemetry and alerts from operational questions and SLOs.
---

# Observability Trajectory

When `/observability` is invoked, preserve all trailing text as task input;
otherwise use the active reliability question.

1. Read `../skills/observability-design/SKILL.md`.
2. Inspect journeys, boundaries, failures, existing telemetry, cardinality,
   correlation, privacy, retention, alerts, and ownership.
3. Specify only signals that answer a concrete operational decision.
4. Keep design read-only unless instrumentation is requested; never mutate
   production telemetry.
5. Return the signal catalog, alerts, runbook needs, costs, and validation
   scenarios concisely without inventing detection.
