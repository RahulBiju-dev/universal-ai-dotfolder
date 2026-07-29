---
name: map
description: Route workspace files through the architecture-mapper skill to produce Mermaid topology.
---

# Map Trajectory

When `/map` is invoked, resolve trailing text as a repository root or use the
current workspace.

1. Read `../skills/architecture-mapper/SKILL.md`.
2. Invoke `../skills/architecture-mapper/map_repo.py`.
3. Verify internal imports, C headers, definitions, and resolvable call edges.
4. Preserve cycles and label static call relationships as inferred.
5. Return one valid Mermaid flowchart and a concise risk summary.

Keep the workflow read-only.
