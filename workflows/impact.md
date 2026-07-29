---
name: impact
description: Map a proposed change across consumers, compatibility, rollout, and validation.
---

# Change-Impact Trajectory

When `/impact` is invoked, preserve all trailing text as task input; otherwise
use the current diff or active proposal.

1. Read `../skills/change-impact-analyzer/SKILL.md`.
2. Inspect definitions, callers, consumers, tests, schemas, configuration,
   build, deployment, persistence, and generated edges.
3. Classify direct, transitive, conditional, and operational impacts.
4. Keep analysis read-only unless implementation is explicitly requested.
5. Return the impact matrix, validation order, rollout constraints, and blind
   spots concisely without claiming complete consumer coverage.
