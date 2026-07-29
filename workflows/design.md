---
name: design
description: Compare architecture options and issue a reversible decision recommendation.
---

# Architecture Decision Trajectory

When `/design` is invoked, preserve all trailing text as task input; otherwise
use the active architecture question.

1. Read `../skills/architecture-decision/SKILL.md`.
2. Inspect current boundaries, data flow, deployment, quality attributes, and
   binding constraints.
3. Compare viable options using explicit evidence, consequences, and
   reversibility.
4. Keep analysis read-only unless an artifact or implementation is requested.
5. Return the recommendation, rejected alternatives, assumptions, and review
   triggers concisely without inventing consensus.
