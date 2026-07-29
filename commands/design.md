---
description: Evaluate consequential architecture options and recommend a reversible decision.
argument-hint: design problem, constraints, quality attributes, and options
---

# Decide Architecture

Preserve all text following `/design` as task input. When empty, use the active
architecture decision under discussion.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/architecture-decision/SKILL.md`.
2. Inspect current boundaries, data flow, deployment shape, operational
   evidence, and binding constraints.
3. Follow the skill's option comparison, reversibility, quality gates, and
   decision-ready output contract.
4. Remain read-only unless the task explicitly requests an ADR or implementation
   after the decision.

Report the recommendation, rejected alternatives, consequences, evidence, and
review triggers concisely. Separate verified constraints from inferred
tradeoffs and never invent consensus.
