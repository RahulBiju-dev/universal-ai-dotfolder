---
description: Configure and run bounded compiler sanitizers against an explicit native target.
argument-hint: C or C++ sources, build command, sanitizer class, inputs, and timeout
---

# Run Sanitizers

Preserve all text following `/sanitize` as task input. When empty, require an
explicit local target and desired sanitizer.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/sanitizer-runner/SKILL.md`.
2. Inspect toolchain, build flags, target inputs, existing artifacts, runtime
   side effects, symbolization, suppressions, and test commands.
3. Follow the skill's isolated build, bounded execution, triage, decision
   boundaries, quality gates, and output contract.
4. Do not edit source unless a fix is requested; ask before installing tools,
   executing unfamiliar code, or using privileged settings.

Report exact commands, sanitizer findings, stack evidence, reproducibility, and
limits concisely. Never describe unrun sanitizers or suppressed output as clean.
