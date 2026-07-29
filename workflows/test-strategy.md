---
name: test-strategy
description: Build a risk-based behavior-to-test matrix across efficient test layers.
---

# Test-Strategy Trajectory

When `/test-strategy` is invoked, preserve all trailing text as task input;
otherwise use the active change and acceptance criteria.

1. Read `../skills/test-strategy/SKILL.md`.
2. Inspect contracts, failure modes, architecture, current tests, historical
   defects, environments, and execution cost.
3. Allocate risks across unit, integration, contract, property, fuzz, fault,
   concurrency, and system layers.
4. Keep strategy read-only; generate tests only through an explicit request.
5. Return priorities, fixtures, gates, and known coverage limits concisely
   without claiming unrun results.
