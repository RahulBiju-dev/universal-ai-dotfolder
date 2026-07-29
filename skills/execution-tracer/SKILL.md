---
name: execution-tracer
description: Trace program execution with bounded, question-driven instrumentation across calls, syscalls, processes, files, allocations, and timing. Use for opaque runtime failures, unexpected I/O, control-flow discovery, syscall tracing, profiling traces, or evidence-backed debugging.
---

# Execution Tracer

## Define the Question

1. State one observable question the trace must answer.
2. Capture the exact command, input, build, environment assumptions, and expected versus actual behavior.
3. Choose the least invasive available layer: application logging, debugger, syscall tracer, profiler, or packet capture.
4. Define event filters, duration, output size, redaction, and stop conditions before execution.

## Collect Evidence

- Build with symbols when needed while preserving optimization assumptions relevant to the bug.
- Trace only the target process tree, functions, files, syscalls, or intervals needed.
- Record monotonic timestamps, process and thread identity, return values, and causal identifiers.
- Keep stdout, stderr, trace output, and program artifacts separate.
- Handle early exit, timeout, signal termination, child processes, and tool failure.
- Store traces in a bounded temporary or task-local location and clean them when no longer needed.

## Analyze and Teach

- Reconstruct the shortest event sequence from trigger to divergence.
- Correlate trace events with source and reject chronology-only causal claims.
- Compare one failing run with a controlled successful run when available.
- Explain each selected trace layer and what it can and cannot observe.
- Teach the student to move from symptom, to hypothesis, to discriminating event, to conclusion.
- Add targeted instrumentation or a regression only after evidence identifies the boundary.

## Safety Boundaries

- Obtain approval before attaching to unrelated processes, using privileges, capturing network traffic, or tracing sensitive data.
- Never expose secrets, personal data, raw environment dumps, or unrelated process activity.
- Avoid unbounded traces and account for observer effects on timing-sensitive programs.
- Do not execute unfamiliar or untrusted targets without an appropriate sandbox.

## Output Contract

- Lead with the answered question and cite the decisive event sequence.
- Report command, filters, duration, environment, and exact tool failures.
- Distinguish observed facts, inference, remaining hypotheses, and tracing gaps.
