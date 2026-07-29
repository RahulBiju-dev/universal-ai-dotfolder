---
name: mutate
description: Measure test fault detection with bounded mutation and survivor triage.
---

# Mutation-Test Trajectory

When `/mutate` is invoked, preserve all trailing text as task input; otherwise
require a target, deterministic test command, and time budget.

1. Read `../skills/mutation-tester/SKILL.md`.
2. Inspect test stability, target criticality, tooling, operators,
   equivalent-mutant risk, limits, and workspace state.
3. Establish the baseline, run bounded mutations, and triage survivors.
4. Restore production source after execution; add tests only when requested and
   ask before installation.
5. Return killed, surviving, equivalent, timed-out, and untested cases concisely
   without fabricating a score.
