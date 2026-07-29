---
name: release
description: Classify release evidence and issue a defensible readiness verdict.
---

# Release-Readiness Trajectory

When `/release` is invoked, preserve all trailing text as task input; otherwise
request the exact candidate and release scope.

1. Read `../skills/release-readiness/SKILL.md`.
2. Inspect candidate identity, changes, artifacts, tests, security,
   compatibility, migrations, observability, documentation, rollout, and rollback.
3. Classify every gate as passed, failed, conditional, not run, or inapplicable.
4. Keep assessment read-only; never tag, sign, publish, push, or deploy.
5. Return the verdict, evidence, blockers, accepted risks, and post-release
   checks concisely; never treat an unrun gate as passed.
