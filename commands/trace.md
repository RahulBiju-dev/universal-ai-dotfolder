---
description: Trace question-driven execution across calls, syscalls, resources, and timing.
argument-hint: target program or path, input, question, trace scope, and execution limits
---

# Trace Execution

Preserve all text following `/trace` as task input. When empty, request the
target and the concrete runtime question.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/execution-tracer/SKILL.md`.
2. Inspect code, build mode, entry point, inputs, processes, files, permissions,
   available tracers, side effects, and expected behavior.
3. Follow the skill's bounded instrumentation, correlation, decision boundaries,
   quality gates, and output contract.
4. Keep source unchanged unless instrumentation edits are requested; ask before
   privileged tracing or executing unfamiliar code.

Return the event timeline, causal path, observed evidence, inference, and
remaining gaps concisely. Never fabricate calls, syscalls, timing, or trace
coverage.
