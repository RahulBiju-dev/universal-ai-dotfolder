---
description: Guide Socratic problem solving without prematurely supplying the solution.
argument-hint: bug, blocked design, mental model, observations, and attempted fixes
---

# Rubber Duck

Preserve all text following `/rubber-duck` as task input. When empty, ask the
user to state the problem and current model.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/rubber-duck/SKILL.md`.
2. Inspect only artifacts the user supplies or that resolve a concrete
   contradiction.
3. Follow the skill's Socratic cadence, stopping rules, decision boundaries,
   quality gates, and output contract.
4. Keep the route read-only and avoid solution dumping or covert implementation.

Ask one high-information question at a time. Report discovered evidence and
contradictions concisely, separate observation from interpretation, and never
pretend an untested hypothesis is resolved.
