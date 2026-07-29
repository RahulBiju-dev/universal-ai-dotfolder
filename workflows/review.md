---
name: review
description: Produce severity-ranked, evidence-backed findings for a concrete change.
---

# Code-Review Trajectory

When `/review` is invoked, preserve all trailing text as task input; otherwise
use the current diff or active target.

1. Read `../skills/code-review/SKILL.md`.
2. Inspect the complete change plus callers, contracts, tests, configuration,
   errors, security, performance, compatibility, and cleanup.
3. Verify suspected findings and rank them by impact, confidence, and reachability.
4. Keep review read-only unless fixes are explicitly requested.
5. Return concise findings with location, scenario, evidence, impact, and
   remediation; never fabricate tests or reproduction.
