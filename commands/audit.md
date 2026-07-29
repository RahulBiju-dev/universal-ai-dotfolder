---
description: Audit code for memory errors, resource leaks, unsafe operations, and complexity bottlenecks.
argument-hint: C source files or code targets
---

# Audit Reliability

Treat the text following `/audit` as target paths; when empty, use the active
file or current diff.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/code-griller/SKILL.md` and run the static analysis first.
2. For explicit C sources, read its `skills/mem-leak-auditor/SKILL.md`, compile with
   strict warnings, and run the bounded Valgrind wrapper.
3. Trace allocation and release, descriptors, locks, threads, subprocesses,
   error paths, bounds, integer sizes, and data-dependent nested work.
4. Distinguish observed runtime evidence from static risk and inference.

Report a compact severity table with `path:line`, evidence, consequence, and
remediation. Do not edit source unless fixes were requested. Never describe
Valgrind execution as a sandbox.
