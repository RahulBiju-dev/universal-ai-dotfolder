---
description: Design a risk-based verification strategy across complementary test layers.
argument-hint: behavior, architecture, risks, constraints, existing tests, and release stage
---

# Design Test Strategy

Preserve all text following `/test-strategy` as task input. When empty, use the
active feature or change and its acceptance criteria.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/test-strategy/SKILL.md`.
2. Inspect contracts, failure modes, architecture, current coverage, historical
   defects, environments, and test cost.
3. Follow the skill's risk ranking, layer selection, decision boundaries,
   quality gates, and output contract.
4. Keep strategy design read-only; generate tests only through a separate
   explicit implementation request.

Return a concise behavior-to-test matrix, priorities, fixtures, gates, and
coverage limits. Do not equate test count or line coverage with validated
behavior, and never claim unrun results.
