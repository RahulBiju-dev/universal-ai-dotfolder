---
description: Scaffold a bounded project or component without overwriting or silent installation.
argument-hint: empty target directory, language or runtime, component goal, and constraints
---

# Bootstrap Project

Preserve all text following `/bootstrap` as task input. When empty, require an
explicit target and project objective.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/project-bootstrapper/SKILL.md`.
2. Inspect the target, parent conventions, tool availability, supported
   environments, build, test, configuration, and documentation expectations.
3. Follow the skill's scaffold selection, collision checks, decision boundaries,
   quality gates, and output contract.
4. Create files only for an explicit empty or approved target; never overwrite,
   install dependencies, initialize remotes, or publish silently.

Report created paths, chosen conventions, local validation, and next commands
concisely. Never claim dependencies, builds, or tests succeeded unless run.
