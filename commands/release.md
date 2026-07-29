---
description: Produce an evidence-based go, conditional-go, or no-go release assessment.
argument-hint: candidate commit or artifact, scope, environments, gates, and release constraints
---

# Assess Release Readiness

Preserve all text following `/release` as task input. When empty, request the
exact candidate and release scope.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/release-readiness/SKILL.md`.
2. Inspect candidate identity, changes, artifacts, tests, security,
   compatibility, migrations, observability, documentation, rollout, and rollback.
3. Follow the skill's gate classification, decision boundaries, quality gates,
   and output contract.
4. Keep assessment read-only; never tag, sign, publish, push, or deploy.

Return the verdict, passed and missing evidence, blockers, owners, accepted
risks, and post-release checks concisely. Treat every unrun mandatory gate as
not run, never passed.
