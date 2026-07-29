---
name: trace
description: Capture a bounded execution timeline that answers one runtime question.
---

# Execution-Trace Trajectory

When `/trace` is invoked, preserve all trailing text as task input; otherwise
request the target and concrete runtime question.

1. Read `../skills/execution-tracer/SKILL.md`.
2. Inspect entry points, inputs, build mode, processes, files, permissions,
   side effects, expected behavior, and available tracers.
3. Select minimal instrumentation and correlate calls, syscalls, resources, and
   timing.
4. Keep source unchanged unless instrumentation is requested; ask before
   privileged tracing or unfamiliar execution.
5. Return observed timeline, causal path, inference, and gaps concisely without
   fabricating trace coverage.
