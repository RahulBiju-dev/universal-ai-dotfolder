---
description: Build a blameless incident postmortem from primary evidence and uncertainty.
argument-hint: incident scope, impact, timestamps, telemetry, changes, and response records
---

# Write Incident Postmortem

Preserve all text following `/postmortem` as task input. When empty, request the
incident scope and available evidence.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/incident-postmortem/SKILL.md`.
2. Inspect timelines, telemetry, tickets, changes, communications, response
   actions, impact evidence, and recovery records.
3. Follow the skill's causal analysis, blameless boundaries, quality gates, and
   output contract.
4. Keep evidence and source systems read-only unless corrective implementation
   is separately requested.

Return impact, timeline, causal chain, response review, and verifiable actions
concisely. Mark estimates, disputes, inference, and missing evidence; never
invent timestamps, causes, owners, or completed actions.
