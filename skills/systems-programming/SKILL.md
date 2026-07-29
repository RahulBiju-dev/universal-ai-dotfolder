---
name: systems-programming
description: Design, implement, and review low-level software with explicit ownership, bounded resource use, safe binary handling, and correct operating-system interactions. Use for C, C++, Rust, POSIX, memory management, file descriptors, processes, signals, IPC, binary formats, or performance-sensitive systems code.
---

# Systems Programming

## Establish the Contract

1. Inspect the target platform, language standard, compiler, build flags, public ABI, and nearby tests.
2. State input bounds, ownership, lifetimes, concurrency assumptions, and observable failure behavior.
3. Trace every allocation, handle, mapping, lock, thread, subprocess, and temporary file from acquisition to release.
4. Define behavior for empty, maximum, malformed, interrupted, and partially initialized inputs.

## Implement or Review

- Use scoped cleanup, RAII, or one auditable cleanup path.
- Check allocation, arithmetic, indexing, conversions, pointer movement, and system-call results.
- Handle short reads, short writes, `EINTR`, cancellation, timeouts, and idempotent shutdown where applicable.
- Keep pointers within one valid object domain and avoid unaligned, aliased, or lifetime-invalid access.
- Specify byte order, alignment, width, and overflow rules at binary boundaries.
- Bound queues, recursion, retries, buffers, threads, and subprocess output.
- Separate parsing, privileged operations, storage, transport, and presentation behind narrow interfaces.
- Add focused tests for success, boundary, failure, and cleanup paths.

## Teach the Engineering

- Explain the governing invariant before the implementation detail.
- Show one concrete failure mechanism and why the chosen design prevents it.
- State time and space complexity for nontrivial paths using the expected input scale.
- Distinguish language guarantees, operating-system behavior, and project convention.
- Give the student one concise checkpoint they can use to review similar code independently.

## Safety Boundaries

- Never execute unfamiliar binaries, use elevated privileges, or weaken compiler protections without explicit approval.
- Never construct shell commands from untrusted input or expose secrets through logs and diagnostics.
- Preserve user changes and public behavior unless the task explicitly authorizes alteration.
- Treat sanitizer, debugger, and profiler output as evidence, not proof that all defects are absent.

## Output Contract

- Lead with the implemented result or highest-severity finding.
- Report ownership and cleanup decisions, complexity, edge cases, and exact validation run.
- Label unexecuted checks, platform assumptions, and residual undefined-behavior or portability risks.
