---
description: Design or implement deterministic, least-privilege continuous integration.
argument-hint: CI provider, repository checks, platforms, failures, budget, and target files
---

# Build CI Pipeline

Preserve all text following `/ci` as task input. When empty, use the active
pipeline request and existing CI configuration.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/ci-pipeline-builder/SKILL.md`.
2. Inspect workflows, permissions, events, jobs, matrices, caches, artifacts,
   secrets, required gates, failure output, and local commands.
3. Follow the skill's pipeline design, decision boundaries, quality gates, and
   output contract.
4. Edit workflow files only when implementation is requested; never trigger,
   approve, or mutate remote CI without authorization.

Report jobs, permissions, cache keys, gates, local validation, and unresolved
provider risks concisely. Never claim a hosted run passed unless observed.
