---
description: Reference slash route demonstrating how a command binds to a skill contract.
argument-hint: goal, target files, constraints, and the exact output you expect
---

# Example Route

Preserve all text following `/example` as task input. When empty, use the active
request and the surrounding repository context.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/example-skill/SKILL.md`.
2. Inspect the files, configuration, tests, and repository state the task names.
3. Follow the skill's workflow, decision boundaries, quality gates, and output
   contract.
4. Edit files only when the task requests implementation; otherwise return the
   analysis the contract specifies.

Report changed artifacts, validation evidence, and unrun checks concisely. Do not
claim a check passed unless it ran.
