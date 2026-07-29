---
name: ci
description: Build deterministic CI jobs with least privilege and actionable failures.
---

# CI Trajectory

When `/ci` is invoked, preserve all trailing text as task input; otherwise use
the active pipeline request and configuration.

1. Read `../skills/ci-pipeline-builder/SKILL.md`.
2. Inspect events, permissions, jobs, matrices, caches, artifacts, secrets,
   gates, failure output, and equivalent local commands.
3. Design deterministic ordering, bounded matrices, and safe cache keys.
4. Edit workflow files only when requested; never trigger or approve remote CI.
5. Return jobs, permissions, gates, local validation, and provider unknowns
   concisely without fabricating hosted results.
