---
name: project-bootstrapper
description: "Scaffold a new software project or bounded component with coherent structure, build, tests, configuration, and documentation. Use when starting from an empty or approved target directory and a minimal production-grade foundation is needed without overwriting files or installing dependencies silently."
---

# Project Bootstrapper
Create the smallest runnable foundation that makes ownership, interfaces, and verification obvious.

## Workflow
1. Inspect the explicit target, workspace instructions, repository state, existing files, and supported runtime.
2. Confirm the objective, language, entry points, deployment shape, constraints, and acceptance command.
3. Choose conventional tooling already available in the workspace and justify nonstandard choices.
4. Design a minimal module tree with separated core logic, adapters, configuration, and tests.
5. Create one complete vertical slice with explicit errors, cleanup, and bounded input behavior.
6. Add reproducible build, format, lint, test, ignore, and environment-example configuration as applicable.
7. Validate syntax, discovery, tests, and the documented startup path using available local tools.

## Decision Boundaries
- Never overwrite a nonempty target or user file without explicit authorization.
- Do not initialize remote services, install dependencies, create credentials, commit, or publish without approval.
- Do not add frameworks, containers, databases, or CI unless the requirements justify them.
- Use `architecture-decision` when foundational choices have materially different long-term consequences.
- Stop when the target path, supported environment, or destructive impact is ambiguous.

## Quality Gates
- Keep generated code complete, executable, and free of placeholder logic.
- Make dependency direction, resource ownership, and public interfaces testable.
- Include success, boundary, failure, and regression test structure from the first slice.
- Use safe defaults, deterministic configuration, and secret-free examples.
- Verify every claimed command result or label it as not run.

## Output Contract
- Show the resulting tree and summarize each top-level responsibility.
- List created and preserved paths explicitly.
- State architecture choices, complexity risks, and deferred decisions.
- Report commands executed with outcomes and environment limits.
- Provide the next smallest feature step without expanding the scaffold.
