---
name: sanitizer-runner
description: Configure, run, and interpret compiler sanitizers for memory errors, undefined behavior, data races, leaks, and uninitialized reads. Use for C or C++ sanitizer builds, crash diagnosis, suspicious pointer behavior, concurrency defects, or validation of low-level fixes.
---

# Sanitizer Runner

## Select the Instrumentation

1. Inspect the compiler, build system, optimization level, debug symbols, test entry points, and platform support.
2. Map the suspected defect to AddressSanitizer, UndefinedBehaviorSanitizer, ThreadSanitizer, LeakSanitizer, or MemorySanitizer.
3. Avoid incompatible combinations and document runtime options that affect reporting.
4. Preserve a normal build path and isolate generated sanitizer artifacts.

## Build and Run

- Use project-native build controls before injecting ad hoc flags.
- Preserve frame pointers and useful symbols when supported.
- Run the smallest deterministic reproducer first, then the focused test suite.
- Bound wall time, memory, test parallelism, logs, and generated cores.
- Capture the complete first report, command, exit status, and relevant build identity.
- Symbolize against the exact instrumented binary.
- Suppress only confirmed external noise with a narrow, documented rule.

## Interpret and Teach

- Identify the first invalid operation, allocation or synchronization origin, and violated lifetime or ordering invariant.
- Separate the primary report from secondary crashes and cleanup fallout.
- Re-run after the fix using the same build and input, then run nearby regressions.
- Explain shadow memory, instrumentation overhead, and false-negative conditions to the student.
- Distinguish a clean observed run from proof of correctness.

## Safety Boundaries

- Never run unfamiliar binaries, privileged targets, production workloads, or unbounded suites without explicit approval.
- Never disable protections or broadly suppress project-owned findings.
- Never mix instrumented and incompatible runtime objects silently.
- Preserve user build configuration and unrelated artifacts.

## Output Contract

- Report sanitizer, compiler flags, target, input, exit status, and the first causal stack.
- State the violated invariant, proposed or applied fix, and exact reruns.
- Label unsupported sanitizers, skipped tests, symbolization gaps, and residual risk.
