---
description: Find reachable boundary, malformed-input, partial-failure, and recovery gaps.
argument-hint: interface, function, module, diff, or behavior to challenge
---

# Hunt Edge Cases

Preserve all text following `/edge-cases` as task input. When empty, use the
active file or current diff.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/edge-case-hunter/SKILL.md`.
2. Inspect contracts, callers, validation, cleanup, tests, state transitions,
   numerical limits, and concurrency where relevant.
3. Follow the skill's reachability ranking, decision boundaries, quality gates,
   and output contract.
4. Keep analysis read-only unless fixes or tests are explicitly requested.

Report a concise severity-ranked case table with trigger, expected safe behavior,
evidence, and coverage. Separate confirmed gaps from inferred risks and never
claim a case is handled without validation.
