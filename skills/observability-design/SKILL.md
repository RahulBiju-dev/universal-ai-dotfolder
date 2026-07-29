---
name: observability-design
description: Design metrics, structured logs, traces, correlation, dashboards, alerts, and runbooks around user-visible reliability and diagnostic questions. Use for missing telemetry, noisy alerts, high-cardinality signals, incident blind spots, SLO instrumentation, or observability reviews.
---

# Observability Design

Derive each signal from a concrete operational question rather than instrumenting indiscriminately.

## Workflow

1. Define critical user journeys, service boundaries, failure modes, and reliability objectives.
2. List the decisions operators must make during normal operation and incidents.
3. Map metrics, events, logs, and spans to those questions with explicit dimensions.
4. Define correlation identifiers and propagation across process and asynchronous boundaries.
5. Set aggregation, sampling, retention, redaction, and cardinality budgets.
6. Design symptom-based alerts with thresholds, evaluation windows, ownership, and runbook actions.
7. Validate signal usefulness against representative success, degradation, and failure scenarios.

## Decision Boundaries

- Keep assessment and design read-only unless instrumentation changes are explicitly requested.
- Do not log secrets, credentials, personal data, raw payloads, or unbounded identifiers.
- Prefer user-impact signals over implementation-detail alerts.
- Separate telemetry design from vendor procurement or production configuration changes.
- Treat dashboards without a decision or owner as non-requirements.

## Quality Gates

- Give every signal a name, type, unit, source, dimensions, and intended question.
- Bound label cardinality and event volume before adoption.
- Align alerts with actionable ownership and suppress duplicate symptom noise.
- Preserve trace and log context through retries, queues, and fan-out.
- Never claim telemetry exists or detects a condition without verification.

## Output Contract

- Return a signal catalog, correlation plan, alert table, and dashboard or runbook outline.
- Identify privacy, cost, retention, and cardinality risks.
- Separate existing evidence from proposed instrumentation.
- State validation scenarios, missing signals, and operational assumptions.
