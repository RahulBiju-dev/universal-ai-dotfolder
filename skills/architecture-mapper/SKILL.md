---
name: architecture-mapper
description: Build a deterministic Mermaid flowchart from Python imports and calls plus C or C++ includes, definitions, and resolvable calls. Use for repository topology, dependency mapping, architecture review, cycle discovery, or copy-pasteable system diagrams.
---

# Architecture Mapper

1. Resolve the repository root inside the active workspace.
2. Run:

   ```text
   python3 map_repo.py --root WORKSPACE
   ```

3. Return the Mermaid output unchanged, then summarize only material dependency
   direction, cycles, hubs, or unresolved edges.
4. Describe call edges as statically inferred.

Never import, compile, or execute source. The mapper skips symlinks, secrets,
generated dependencies, binaries, oversized files, and unsupported syntax. A
truncated graph must retain its truncation marker.
