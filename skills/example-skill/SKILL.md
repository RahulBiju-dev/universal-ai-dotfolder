---
name: example-skill
description: "Reference skill package demonstrating the on-demand skill contract, its reference layout, and its executable utility pattern. Use when authoring a new skill and you need a validated structural example to copy."
---

# Example Skill
Demonstrate the operating contract every skill package follows so a new skill
starts from a validated shape instead of an empty file.

## Workflow
1. Inspect workspace instructions, repository state, and the files named by the
   request before forming any conclusion.
2. Restate the observable goal, the in-scope surfaces, and the exclusions.
3. Identify invariants, public contracts, consumers, and destructive transitions.
4. Perform the narrowest work that satisfies the goal, leaving the repository
   coherent at each step.
5. Verify with the cheapest relevant check first, then the authoritative one.

## Decision Boundaries
- Read `references/example-reference.md` only when the deeper structural detail
  is actually needed; keep this contract loaded on its own otherwise.
- Do not edit files, install dependencies, or mutate external systems unless the
  request explicitly asks for it.
- Do not invent interfaces, commands, owners, or requirements.
- Stop for clarification when alternatives change public behavior or
  irreversible state.

## Quality Gates
- Ensure every step produces an observable artifact or verified state change.
- Cover the normal, empty, boundary, and failure paths where they apply.
- Label proposed commands as unexecuted until their results are observed.
- Remove speculative work that does not advance an acceptance criterion.

## Utility
Resolve the skill directory as the directory containing this file, then run:

```text
python3 example_utility.py --root WORKSPACE
```

It prints a deterministic inventory of the scaffold. Read `truncated` and the
skipped counters before assuming the listing is complete.

## Output Contract
- State the goal, scope, and assumptions first.
- Report findings with `path:line`, consequence, and repair where applicable.
- Rank material risks and name the evidence needed to close each one.
- Distinguish inspected facts, recommendations, and unvalidated expectations.
