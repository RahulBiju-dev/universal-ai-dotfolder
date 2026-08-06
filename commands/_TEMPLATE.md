---
description: One sentence stating what invoking this route does, phrased as an action.
argument-hint: the inputs a user should type after the slash name
---

# Route Title

Preserve all text following `/replace-with-filename-stem` as task input. When
empty, use the active request and the surrounding repository context.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/replace-with-skill-name/SKILL.md`.
2. Inspect the code, configuration, tests, and repository state the task names.
3. Follow that skill's workflow, decision boundaries, quality gates, and output
   contract.
4. Edit files only when the task requests implementation; otherwise return the
   analysis the contract specifies.

Report changed artifacts, validation evidence, and unrun checks concisely.

Pair this file with `workflows/<same-basename>.md`, which must reference the same
skill contract. The validator rejects an unpaired route or a mismatched target.
