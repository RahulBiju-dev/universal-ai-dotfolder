---
description: Review a concrete change for severity-ranked defects and regression risk.
argument-hint: diff, commit, pull request patch, target files, or active change
---

# Review Code

Preserve all text following `/review` as task input. When empty, use the current
diff or active code target.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/code-review/SKILL.md`.
2. Inspect the complete change plus contracts, callers, tests, configuration,
   errors, security, performance, compatibility, and cleanup.
3. Follow the skill's severity ranking, decision boundaries, quality gates, and
   output contract.
4. Keep review read-only unless fixes are explicitly requested.

Lead with concise findings containing location, scenario, impact, evidence, and
remediation. Separate defects from optional improvements and never claim tests,
reproduction, or safety without validation.
