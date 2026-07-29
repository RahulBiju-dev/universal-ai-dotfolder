---
description: Produce a deterministic Mermaid map of repository dependencies and inferred calls.
argument-hint: repository or source directory
---

# Map Architecture

Treat the text following `/map` as the repository root; when empty, use the
current workspace.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/architecture-mapper/SKILL.md`.
2. Run the sibling skill's `map_repo.py` on the resolved root.
3. Validate that file, import, include, definition, and call edges match source.
4. Label static call edges as inferred and retain cycles.

Return one copy-pasteable Mermaid flowchart followed by at most five concise
architectural observations. Do not modify the repository.
