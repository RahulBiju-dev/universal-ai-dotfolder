---
name: repo-search
description: Perform deterministic, ranked, tokenized search across repository source and configuration files with file, size, secret, symlink, and result bounds. Use to locate implementations, symbols, definitions, callers, configuration, or architectural evidence without indexing or changing the workspace.
---

# Repository Search

Resolve the skill directory as the directory containing this file, then run:

```text
python3 search.py "query terms" --root WORKSPACE
```

Use `--case-sensitive`, `--definitions-only`, or bounded result and file limits
only when the request needs them.

Read ranked matches as `path`, `line`, `score`, `kind`, and `text`. Check
`truncated`, skipped counters, and errors before assuming completeness.

Keep searches read-only. Never follow symlinks or inspect secret-bearing,
dependency, generated, binary, or oversized files.
