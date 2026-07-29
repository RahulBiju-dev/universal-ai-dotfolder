---
name: dependency-upgrader
description: Plan and safely implement explicitly requested package, library, runtime, compiler, action, or toolchain upgrades across manifests and lockfiles. Use for outdated or vulnerable dependencies, major-version adoption, transitive conflicts, deprecations, compatibility review, and upgrade validation.
---

# Dependency Upgrader

Advance dependencies deliberately while preserving reproducibility and supported behavior.

## Workflow

1. Inventory manifests, lockfiles, vendored code, runtime constraints, and every selected version.
2. Define the requested target, supported platforms, compatibility window, and non-goals.
3. Inspect authoritative release notes, migration guides, advisories, and local usage when available.
4. Trace changed APIs, defaults, transitive dependencies, build flags, generated files, and licenses.
5. Plan the smallest coherent upgrade order with rollback points.
6. Update only authorized manifests, lockfiles, code, tests, and documentation.
7. Run focused build, test, lint, compatibility, and artifact checks.

## Decision Boundaries

- Keep assessment read-only unless the user explicitly requests the upgrade.
- Treat an upgrade request as write authority only for the named dependency and necessary adaptations.
- Ask before network access, package installation, credential use, or remote mutation.
- Avoid unrelated version churn and never regenerate lockfiles without inspecting the delta.
- Distinguish verified compatibility evidence from inferred downstream risk.
- Use `skills/shell-exec/exec.py` for bounded local validation when dependencies are already available.

## Quality Gates

- Record old and new direct plus resolved versions.
- Explain every source or configuration adaptation caused by the upgrade.
- Check platform, runtime, API, ABI, schema, and persisted-data compatibility as applicable.
- Preserve deterministic resolution and verify rollback feasibility.
- Never claim an advisory is fixed or tests pass unless verified.

## Output Contract

- Report version deltas, compatibility findings, changed files, and transitive effects.
- List exact validation commands and outcomes.
- Identify manual migrations, deprecated behavior, license changes, and release risks.
- State unavailable release evidence, untested platforms, and remaining blockers.
