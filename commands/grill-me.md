---
description: Expose requirement gaps through a focused pre-implementation question gate.
argument-hint: raw request, proposal, or unresolved decision
---

# Grill Requirements

Preserve all text following `/grill-me` as task input. When empty, use the
active proposal or ask for the request that needs clarification.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/requirement-griller/SKILL.md`.
2. Inspect only context needed to identify material scope, behavior, safety,
   compatibility, cost, and acceptance gaps.
3. Follow the skill's question ordering, stopping rule, decision boundaries,
   quality gates, and output contract.
4. Keep the route read-only and do not begin design or implementation.

Ask only discriminating questions, preserve answered constraints, and report
the resolved execution contract concisely. Distinguish known facts from
assumptions and never fabricate agreement or validation.
