---
name: grill
description: Route active code telemetry through the code-griller skill for a blocking technical review.
---

# Grill Trajectory

When `/grill` is invoked, treat trailing text as target paths; otherwise resolve
the active file or current diff.

1. Capture repository status, selected diff, target interfaces, callers, and
   nearby tests without changing state.
2. Read `../skills/code-griller/SKILL.md`.
3. Execute `../skills/code-griller/grill.py` for the resolved targets.
4. Correlate static findings with the captured code telemetry.
5. Return severity-ranked evidence, the three highest-leverage corrections, and
   a ship or block verdict.

Stop after critique unless code changes are explicitly requested.
