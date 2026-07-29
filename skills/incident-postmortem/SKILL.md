---
name: incident-postmortem
description: Produce blameless, evidence-based postmortems from incident timelines, telemetry, tickets, chat, changes, and response records. Use after outages, security events, data incidents, severe regressions, or near misses to explain impact, contributing conditions, detection, response, recovery, and prevention.
---

# Incident Postmortem

Reconstruct what happened and improve the system without assigning personal blame.

## Workflow

1. Define incident scope, user impact, severity, start, detection, mitigation, recovery, and end criteria.
2. Build a timestamped timeline from primary evidence and identify clock or source uncertainty.
3. Trace the causal chain from triggering conditions through safeguards, propagation, and visible impact.
4. Separate root mechanisms, contributing conditions, response friction, and unrelated observations.
5. Evaluate detection, diagnosis, communication, mitigation, recovery, and decision points.
6. Identify what worked, what failed safely, and where defenses or runbooks were missing.
7. Define outcome-based corrective actions with priority, owner role, verification, and review point.

## Decision Boundaries

- Keep postmortem work read-only unless corrective implementation is explicitly requested.
- Do not alter source evidence, production systems, tickets, or external records without approval.
- Avoid hindsight bias, single-cause stories, personal blame, and unsupported intent.
- Mark disputed, estimated, and missing timeline facts explicitly.
- Separate emergency mitigation from durable corrective action.

## Quality Gates

- Tie causal statements to timeline evidence or label them as inference.
- Quantify impact and duration only from identified sources.
- Address technical, process, detection, and recovery contributors.
- Make actions specific, measurable, risk-reducing, and verifiable.
- Never claim an action is complete or prevention validated unless checked.

## Output Contract

- Return summary, impact, timeline, causal analysis, response review, and corrective actions.
- Include evidence sources and confidence for material conclusions.
- Separate completed mitigation, open actions, accepted risk, and unanswered questions.
- State sensitive details intentionally omitted and any follow-up investigation required.
