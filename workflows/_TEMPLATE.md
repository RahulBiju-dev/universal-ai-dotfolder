---
name: replace-with-filename-stem
description: One sentence stating the trajectory this workflow drives, phrased as an action.
---

# Trajectory Title

When `/replace-with-filename-stem` is invoked, preserve all trailing text as task
input; otherwise use the active request and the surrounding repository context.

1. Read `../skills/replace-with-skill-name/SKILL.md`.
2. Inspect the code, configuration, tests, and repository state the task names.
3. Follow that skill's workflow, decision boundaries, and quality gates before
   producing any output.
4. Mutate files only when implementation is explicit and stay within the target
   surface.
5. Return changed artifacts, validation evidence, and unrun checks concisely.

Pair this file with `commands/<same-basename>.md`, which must reference the same
skill contract. The validator rejects an unpaired route or a mismatched target.
