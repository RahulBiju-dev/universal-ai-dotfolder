# Example Reference

Deep guidance lives here, not in `SKILL.md`. The skill contract stays short so
routing loads little context; a reference is read only when the task needs the
detail it holds.

## When To Add A Reference

Add one when the guidance is long, rarely needed, or genuinely optional. Keep it
out when every use of the skill needs the material, because then it belongs in
the contract itself.

## Structure

- Give the file a task-oriented name that says what the reader will get.
- Lead each section with the decision it supports.
- Prefer tables, checklists, and worked examples over narrative.
- Name the file explicitly from `SKILL.md` so the router knows it exists.

## Constraints

- Keep every local link resolvable from this file's directory.
- Avoid unfinished markers; the workspace validator rejects them.
- Do not restate the contract's workflow, gates, or output rules.
