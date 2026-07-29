---
name: audit
description: Bind static review to strict C compilation and bounded Valgrind memory profiling.
---

# Audit Trajectory

When `/audit` is invoked, resolve trailing paths or the active code target.

1. Read `../skills/code-griller/SKILL.md` and perform the read-only static pass.
2. If every executable target is explicit C source, read
   `../skills/mem-leak-auditor/SKILL.md`.
3. Compile in an isolated temporary directory with strict diagnostics.
4. Run Valgrind with bounded runtime and full leak-kind reporting.
5. Merge compiler, Valgrind, ownership, bounds, and complexity evidence without
   conflating observed failures with inferred risks.
6. Return a dense severity table and remediation order.

Do not change source or describe the execution wrapper as a security sandbox.
