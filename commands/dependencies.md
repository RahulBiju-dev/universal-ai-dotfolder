---
description: Assess or apply a bounded dependency upgrade with compatibility evidence.
argument-hint: package or tool, current and target version, scope, and apply intent
---

# Upgrade Dependencies

Preserve all text following `/dependencies` as task input. When empty, use the
active manifest issue and request the intended package or target.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/dependency-upgrader/SKILL.md`.
2. Inspect manifests, lockfiles, local usage, runtime constraints, transitive
   resolution, release evidence, tests, and licenses.
3. Follow the skill's upgrade ordering, decision boundaries, quality gates, and
   output contract.
4. Default to read-only assessment; edit only for an explicit upgrade request
   and ask before network access or installation.

Report version deltas, adaptations, transitive effects, validation, and rollback
risks concisely. Never claim an advisory is fixed or a platform supported
without evidence.
