---
name: postmortem
description: Reconstruct an incident and define blameless, verifiable corrective actions.
---

# Postmortem Trajectory

When `/postmortem` is invoked, preserve all trailing text as task input;
otherwise request incident scope and primary evidence.

1. Read `../skills/incident-postmortem/SKILL.md`.
2. Inspect impact records, timestamps, telemetry, tickets, changes,
   communications, response actions, and recovery evidence.
3. Build the timeline and causal chain while marking uncertainty and disputes.
4. Keep source evidence read-only unless corrective implementation is separate
   and explicit.
5. Return impact, causes, response review, and verifiable actions concisely
   without blame or invented facts.
