---
name: debug
description: Reproduce a failure and reduce hypotheses to an evidence-backed cause.
---

# Debugging Trajectory

When `/debug` is invoked, preserve all trailing text as task input; otherwise
use the active failure evidence.

1. Read `../skills/debugging-playbook/SKILL.md`.
2. Inspect the symptom, environment, failing path, tests, configuration, recent
   changes, and exact output.
3. Reproduce narrowly, rank hypotheses, and falsify them with discriminating
   checks.
4. Keep diagnosis read-only unless a fix is explicitly requested.
5. Return reproduction status, root cause, evidence, rejected hypotheses, and
   uncertainty concisely without fabricating execution.
