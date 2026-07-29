---
name: security-threat-model
description: Build evidence-based threat models for applications, services, protocols, data flows, infrastructure, agents, and proposed changes. Use for trust-boundary review, abuse-case discovery, authentication or authorization design, sensitive-data handling, attack-surface analysis, or pre-release security planning.
---

# Security Threat Model

Identify reachable attack paths and proportionate controls without performing exploitation.

## Workflow

1. Define the system scope, assets, security objectives, actors, and deployment assumptions.
2. Map entry points, data flows, trust boundaries, identities, privileges, and external dependencies.
3. Enumerate abuse cases for spoofing, tampering, disclosure, denial, escalation, and supply-chain compromise.
4. Trace each credible threat through prerequisites, vulnerable boundary, impact, and existing controls.
5. Rank risks by reachability, likelihood, impact, detectability, and blast radius.
6. Recommend preventive, detective, and recovery controls with testable outcomes.
7. Reassess residual risk and explicit acceptance after proposed controls.

## Decision Boundaries

- Keep threat modeling read-only unless remediation is explicitly requested.
- Do not probe production, third-party, or unauthorized systems.
- Do not expose live secrets, weaponize findings, or fabricate exploitability.
- Separate code-confirmed weaknesses, architecture risks, and assumption-dependent threats.
- Use architecture mapping or repository search only to establish actual boundaries and flows.

## Quality Gates

- Tie every threat to an asset, actor, entry point, and trust transition.
- Credit existing controls and avoid duplicate or generic checklist findings.
- Distinguish vulnerability severity from business impact.
- Include abuse prevention, detection, response, and recovery.
- Never claim a system is secure or a control works without validation.

## Output Contract

- Return a threat table with path, prerequisites, impact, controls, residual risk, and evidence.
- Provide a prioritized mitigation and verification plan.
- Document scope exclusions, assumptions, and accepted risks.
- State which findings require specialist review or safe validation.
