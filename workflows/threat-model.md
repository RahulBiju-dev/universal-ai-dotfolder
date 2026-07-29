---
name: threat-model
description: Map credible abuse paths across assets, actors, boundaries, and controls.
---

# Threat-Model Trajectory

When `/threat-model` is invoked, preserve all trailing text as task input;
otherwise request system scope and protected assets.

1. Read `../skills/security-threat-model/SKILL.md`.
2. Inspect entry points, identities, privileges, data flows, trust transitions,
   dependencies, controls, and deployment assumptions.
3. Rank reachable abuse paths and identify preventive, detective, and recovery
   controls.
4. Keep modeling read-only and never probe unauthorized systems.
5. Return threats, evidence, controls, residual risk, and exclusions concisely
   without fabricating exploitability.
