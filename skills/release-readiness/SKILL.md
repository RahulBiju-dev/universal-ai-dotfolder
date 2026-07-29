---
name: release-readiness
description: Assess whether a change, version, artifact, or service is ready for release using evidence from scope, tests, builds, compatibility, security, migrations, observability, documentation, rollout, and rollback. Use for go or no-go reviews, release checklists, candidate validation, and blocker triage.
---

# Release Readiness

Make a defensible release recommendation without publishing, tagging, or deploying.

## Workflow

1. Define the release scope, candidate identity, target environments, owners, and acceptance gates.
2. Inspect repository state, included changes, artifacts, dependency deltas, and unresolved work.
3. Verify available build, test, lint, security, performance, compatibility, and packaging evidence.
4. Review migrations, configuration, feature flags, observability, runbooks, support, and documentation.
5. Evaluate rollout order, canary or staged exposure, pause criteria, rollback, and data recovery.
6. Classify every gate as passed, failed, conditionally accepted, not run, or not applicable.
7. Produce a go, conditional-go, or no-go recommendation tied to blockers and owners.

## Decision Boundaries

- Keep the assessment read-only unless release fixes are explicitly requested.
- Never tag, sign, publish, push, deploy, or mutate remote state without approval.
- Do not accept verbal confidence as a substitute for required evidence.
- Distinguish release blockers from follow-up improvements.
- Use `skills/git-manager/git_sync.py` for bounded local state and diff evidence and `skills/shell-exec/exec.py` for authorized checks.

## Quality Gates

- Identify the exact commit, version, or artifact under assessment.
- Require rollback feasibility for stateful or compatibility-sensitive changes.
- Treat missing mandatory evidence as not run, never as passed.
- Confirm operator and user-facing failure paths are documented.
- Never claim readiness or validation beyond the inspected candidate.

## Output Contract

- Return the recommendation, gate table, blockers, owners, and required next evidence.
- Report exact commands and artifacts inspected with outcomes.
- Separate verified gates from accepted risks and unknowns.
- State rollout, rollback, monitoring, and post-release verification requirements.
