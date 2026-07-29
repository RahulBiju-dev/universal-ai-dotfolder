---
name: git-manager
description: Summarize local Git state, inspect bounded diffs and commit trees, stage explicit literal paths, and validate configured SSH transport state. Use for concise repository telemetry, selective staging, remote diagnostics, or history inspection without commit, pull, push, reset, or credential management.
---

# Git Manager

Resolve the skill directory as the directory containing this file. Use an
explicit repository:

```text
python3 git_sync.py --repo REPOSITORY state
python3 git_sync.py --repo REPOSITORY diff --staged PATH
python3 git_sync.py --repo REPOSITORY stage PATH
python3 git_sync.py --repo REPOSITORY tree
python3 git_sync.py --repo REPOSITORY ssh
```

Inspect state and diffs before staging. Stage only user-authorized literal paths
and verify the resulting staged stat. Preserve unrelated staged content.

SSH inspection is local by default. Use `ssh --probe REMOTE` only after explicit
authorization for a bounded noninteractive network handshake. The utility
intentionally exposes no commit, pull, push, reset, force, credential, or key
mutation operation.
