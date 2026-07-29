---
name: change-impact-analyzer
description: Trace the direct and transitive blast radius of proposed code, API, schema, configuration, dependency, build, or runtime changes. Use before implementation, review, migration, deprecation, or release when affected consumers, tests, compatibility, rollout, and rollback need evidence.
---

# Change Impact Analyzer

Map consequences before edits so implementation scope and compatibility risk stay explicit.

## Workflow

1. Define the proposed change, preserved invariants, public surface, and intended observable result.
2. Inspect the target definition, references, callers, implementers, generated artifacts, and tests.
3. Trace data, control, configuration, build, packaging, deployment, and persistence dependencies.
4. Identify consumers across processes, repositories, versions, platforms, and operational workflows.
5. Classify impacts as direct, transitive, conditional, compatibility-sensitive, or operational.
6. Model rollout, mixed-version operation, rollback, stale data, cache, and partial-deployment states.
7. Rank required edits and validation by consequence and confidence.

## Decision Boundaries

- Keep analysis read-only unless the user explicitly requests implementation.
- Do not infer a consumer is unaffected merely because textual references are absent.
- Separate current repository evidence from external-consumer assumptions.
- Use `skills/repo-search/search.py` for references and `skills/architecture-mapper/map_repo.py` for broad dependency topology when useful.
- Treat generated code, reflection, registration, configuration, and wire contracts as hidden edges.

## Quality Gates

- Tie every claimed impact to a dependency path or stated assumption.
- Cover interfaces, data formats, tests, documentation, observability, and recovery.
- Identify both required changes and explicitly unaffected critical surfaces.
- Verify compatibility claims against representative old and new states.
- Never claim validation or consumer coverage that was not executed or inspected.

## Output Contract

- Return an impact matrix with surface, dependency path, change required, risk, and evidence.
- Separate confirmed impacts from plausible external impacts.
- Provide an ordered implementation and validation scope.
- State rollout constraints, rollback requirements, blind spots, and residual risk.
