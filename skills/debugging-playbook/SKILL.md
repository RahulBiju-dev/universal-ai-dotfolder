---
name: debugging-playbook
description: Diagnose crashes, hangs, wrong outputs, flaky behavior, test failures, regressions, and environment-specific defects through reproducible evidence and hypothesis reduction. Use when a symptom needs root-cause investigation, a minimal reproducer, or a disciplined debugging plan.
---

# Debugging Playbook

Drive investigation from observable symptoms to the smallest supported causal explanation.

## Workflow

1. Record expected behavior, observed behavior, first known failure, environment, and reproduction inputs.
2. Reproduce the symptom with the narrowest safe command and preserve exact output.
3. Inspect the failing path, nearby tests, configuration, recent changes, and dependency boundaries.
4. Build ranked hypotheses that each predict a differentiating observation.
5. Falsify hypotheses with targeted logging, assertions, probes, or reduced inputs.
6. Locate the earliest incorrect state transition rather than the final visible error.
7. Verify the root cause against the original reproducer and at least one adjacent case.

## Decision Boundaries

- Keep diagnosis read-only unless the user explicitly requests a fix.
- Do not shotgun-edit, suppress errors, weaken assertions, or retry blindly.
- Distinguish reproduced facts, trace-supported inference, and untested hypotheses.
- Use `skills/shell-exec/exec.py` for bounded local reproduction when direct execution is authorized.
- Use `skills/mem-leak-auditor/audit_memory.py` only for explicit C memory-error symptoms and safe local targets.

## Quality Gates

- Require a stable symptom definition before attributing cause.
- Preserve exact commands, inputs, versions, exit codes, and relevant stderr.
- Explain why competing hypotheses were rejected.
- Confirm that the proposed remedy addresses cause rather than masking symptoms.
- Never claim reproduction, resolution, or passing validation unless it ran.

## Output Contract

- Report reproduction status, evidence timeline, root cause, confidence, and affected boundary.
- Provide a minimal fix strategy only when useful or requested.
- List exact validation steps and outcomes.
- State unresolved hypotheses, environmental constraints, and regression risks.
