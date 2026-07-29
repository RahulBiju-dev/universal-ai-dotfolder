---
name: sanitize
description: Build and run an explicit native target under bounded compiler sanitizers.
---

# Sanitizer Trajectory

When `/sanitize` is invoked, preserve all trailing text as task input; otherwise
require an explicit target and sanitizer class.

1. Read `../skills/sanitizer-runner/SKILL.md`.
2. Inspect toolchain, flags, inputs, artifacts, side effects, symbolization,
   suppressions, and existing test commands.
3. Build in an isolated location and execute within declared resource bounds.
4. Keep source unchanged unless a fix is requested; ask before installation or
   unfamiliar execution.
5. Return exact commands, findings, stack evidence, reproducibility, and limits
   concisely without calling an unrun sanitizer clean.
