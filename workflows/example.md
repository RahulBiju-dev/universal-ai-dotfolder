---
name: example
description: Reference trajectory demonstrating how an Antigravity workflow binds to a skill contract.
---

# Example Trajectory

When `/example` is invoked, preserve all trailing text as task input; otherwise
use the active request and the surrounding repository context.

1. Read `../skills/example-skill/SKILL.md`.
2. Inspect the files, configuration, tests, and repository state the task names.
3. Follow the skill's workflow, decision boundaries, and quality gates before
   producing any output.
4. Mutate files only when implementation is explicit and stay within the target
   surface.
5. Return changed artifacts, validation evidence, and unrun checks concisely.
