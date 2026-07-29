---
description: Reduce a runtime or test failure to an evidence-backed root cause.
argument-hint: symptom, target, reproduction command, logs, or failing test
---

# Debug Systematically

Preserve all text following `/debug` as task input. When empty, use the active
failure evidence and ask only for missing reproduction data.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/debugging-playbook/SKILL.md`.
2. Inspect the failing path, tests, configuration, recent changes, exact output,
   and environment before forming hypotheses.
3. Follow the skill's reproduction, falsification, decision boundaries, quality
   gates, and output contract.
4. Keep diagnosis read-only unless a fix is explicitly requested.

Report reproduction status, evidence, rejected hypotheses, root cause, and
residual uncertainty concisely. Never claim reproduction, resolution, or passing
checks that did not run.
