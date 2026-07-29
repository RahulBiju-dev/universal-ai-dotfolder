---
description: Design actionable metrics, logs, traces, alerts, dashboards, and runbooks.
argument-hint: service or journey, SLOs, failure modes, telemetry, and operator questions
---

# Design Observability

Preserve all text following `/observability` as task input. When empty, use the
active service or reliability question.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/observability-design/SKILL.md`.
2. Inspect user journeys, boundaries, failure modes, existing signals,
   cardinality, correlation, retention, privacy, alerts, and ownership.
3. Follow the skill's signal design, decision boundaries, quality gates, and
   output contract.
4. Keep design read-only unless instrumentation changes are explicitly
   requested; never mutate production telemetry.

Return a concise signal catalog, alert and runbook plan, costs, and validation
scenarios. Separate existing evidence from proposed instrumentation and never
claim detection that was not tested.
