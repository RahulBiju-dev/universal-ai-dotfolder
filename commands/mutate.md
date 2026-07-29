---
description: Evaluate test fault detection with bounded mutation testing and mutant triage.
argument-hint: critical target, test command, mutation operators, scope, and time budget
---

# Test with Mutations

Preserve all text following `/mutate` as task input. When empty, require an
explicit target, test command, and execution budget.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/mutation-tester/SKILL.md`.
2. Inspect test determinism, target criticality, available tooling, operators,
   equivalent-mutant risk, time limits, and workspace cleanliness.
3. Follow the skill's baseline, bounded run, survivor triage, decision
   boundaries, quality gates, and output contract.
4. Keep production source unchanged after the run; ask before installation or
   costly execution and add tests only when requested.

Report baseline, operators, killed and surviving mutants, equivalent cases, and
test improvements concisely. Never fabricate mutation scores or hide timeouts.
