---
name: dependencies
description: Assess and apply explicitly requested dependency upgrades with bounded risk.
---

# Dependency-Upgrade Trajectory

When `/dependencies` is invoked, preserve all trailing text as task input;
otherwise request the package and intended target.

1. Read `../skills/dependency-upgrader/SKILL.md`.
2. Inspect manifests, lockfiles, local use, runtime constraints, release
   evidence, transitive resolution, tests, and licenses.
3. Determine version order, required adaptations, and rollback before editing.
4. Default to read-only assessment; ask before network access or installation.
5. Return deltas, transitive effects, validation, and unresolved compatibility
   concisely without claiming unverified advisory resolution.
