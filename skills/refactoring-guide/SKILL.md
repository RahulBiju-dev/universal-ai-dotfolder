---
name: refactoring-guide
description: Plan and, when explicitly requested, execute behavior-preserving refactors that improve boundaries, cohesion, naming, duplication, dependency direction, and testability. Use for extraction, decomposition, decoupling, cleanup, modularization, or staged legacy-code restructuring.
---

# Refactoring Guide

Preserve observable behavior while improving one structural property at a time.

## Workflow

1. Define the refactoring objective, non-goals, invariants, and externally observable behavior.
2. Inspect callers, tests, contracts, ownership, side effects, and current dependency direction.
3. Establish characterization tests or other evidence for behavior at risk.
4. Select the smallest sequence of reversible transformations.
5. Separate moves, renames, and mechanical edits from semantic changes.
6. Validate after each coherent step and review the diff for accidental behavior change.
7. Stop when the stated structural objective is met rather than expanding into redesign.

## Decision Boundaries

- Keep recommendations read-only unless the user explicitly requests refactoring edits.
- Treat a refactor request as authority only for the named scope.
- Do not combine feature work, dependency upgrades, public contract changes, or speculative cleanup.
- Prefer existing project patterns over introducing a new abstraction vocabulary.
- Distinguish observed behavior and test evidence from inferred invariants.
- Use `skills/repo-search/search.py` to confirm references and `skills/shell-exec/exec.py` for authorized focused checks.

## Quality Gates

- State the preserved invariants before changing structure.
- Keep intermediate states buildable or explicitly isolate atomic steps.
- Preserve error behavior, resource lifetime, performance class, and compatibility.
- Require tests at seams where code moves or dependencies invert.
- Never claim behavior preservation unless relevant validation ran.

## Output Contract

- Return the target structure, ordered steps, and rationale for each boundary.
- Report changed artifacts and validation results when implementation was requested.
- Separate mechanical changes from semantic risks.
- State rollback points, deferred cleanup, and remaining coupling.
