---
name: documentation-writer
description: "Create or update concise technical documentation grounded in repository behavior, interfaces, commands, and supported versions. Use for READMEs, how-to guides, references, architecture overviews, runbooks, troubleshooting, or maintenance notes that must remain verifiable and task-oriented."
---

# Documentation Writer
Write for a defined reader and task while tracing every technical claim to current evidence.

## Workflow
1. Inspect the requested audience, documentation location, local style, source, tests, and configuration.
2. Define the reader's goal, prerequisites, supported path, and likely failure points.
3. Choose the smallest useful form such as tutorial, how-to, reference, explanation, or runbook.
4. Organize content in task order and keep concepts separate from command reference.
5. Build complete examples from real interfaces and use inert values for credentials or private data.
6. Verify links, paths, flags, defaults, version claims, and commands where execution is safe and requested.
7. Review the diff for duplicated truth, stale instructions, ambiguity, and unsupported promises.

## Decision Boundaries
- Use `adr-writer` to record an architecture decision and its consequences.
- Do not invent features, support guarantees, command output, benchmarks, or validation results.
- Do not copy secrets, personal data, raw environment dumps, or unsafe commands into examples.
- Prefer linking to one authoritative definition over duplicating volatile details.
- Ask for the intended audience only when it materially changes structure or terminology.

## Quality Gates
- Make every example internally complete, copyable, and clearly scoped.
- Distinguish required steps, optional alternatives, warnings, and expected results.
- Explain why a non-obvious constraint exists without narrating routine mechanics.
- Keep terminology, names, paths, and version boundaries consistent with source.
- Label unexecuted commands and environment-specific behavior explicitly.

## Output Contract
- State the audience, task, and authoritative evidence used.
- Return the finished documentation or a focused patch, not an outline unless requested.
- List changed documentation paths and any source conflicts discovered.
- Report executed checks separately from manual review.
- Identify remaining unknowns, stale adjacent docs, and ownership follow-ups.
