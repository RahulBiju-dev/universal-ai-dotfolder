---
description: Map trust boundaries, credible attack paths, controls, and residual risk.
argument-hint: system or change, assets, actors, deployment, and security objectives
---

# Build Threat Model

Preserve all text following `/threat-model` as task input. When empty, use the
active design and ask for its protected assets.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/security-threat-model/SKILL.md`.
2. Inspect assets, entry points, identities, privileges, data flows, trust
   transitions, dependencies, controls, and deployment assumptions.
3. Follow the skill's abuse-case analysis, risk ranking, decision boundaries,
   quality gates, and output contract.
4. Keep modeling read-only; never probe unauthorized or production systems.

Return a concise threat table, prioritized controls, verification plan, scope
exclusions, and residual risk. Separate confirmed weaknesses from
assumption-dependent threats and never fabricate exploitability.
