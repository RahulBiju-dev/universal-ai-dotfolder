---
description: Measure and interpret coverage to locate risky unexercised behavior.
argument-hint: test command, target paths, coverage type, baseline, and gate intent
---

# Analyze Coverage

Preserve all text following `/coverage` as task input. When empty, use the
project's existing coverage configuration or request a test command.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/coverage-analyzer/SKILL.md`.
2. Inspect test layout, instrumentation, exclusions, generated code, source maps,
   prior reports, changed code, and risk boundaries.
3. Follow the skill's measurement, interpretation, decision boundaries, quality
   gates, and output contract.
4. Keep source and tests unchanged unless additions are requested; ask before
   installing coverage tooling.

Report executed commands, coverage dimensions, high-risk gaps, misleading
instrumentation, and next tests concisely. Never equate a percentage with
correctness or fabricate an unrun report.
