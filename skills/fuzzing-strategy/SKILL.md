---
name: fuzzing-strategy
description: Plan and implement bounded fuzz testing for parsers, binary formats, protocol handlers, unsafe interfaces, and security-sensitive input paths. Use for fuzz harnesses, corpus design, dictionaries, sanitizer combinations, crash triage, coverage plateaus, or continuous fuzzing strategy.
---

# Fuzzing Strategy

## Select the Target

1. Map untrusted input boundaries and rank targets by reachability, consequence, and parser depth.
2. Choose the narrowest deterministic entry point that exercises meaningful logic.
3. Define accepted input size, runtime, memory, recursion, and side-effect limits.
4. Record the expected oracle: crash, sanitizer finding, timeout, invariant breach, or differential mismatch.

## Build the Harness

- Reset global state between cases and make setup cheaper than the target path.
- Consume bytes without out-of-bounds reads or accidentally constraining away malformed inputs.
- Stub network, time, randomness, subprocesses, and persistent writes.
- Seed the corpus with minimal valid structures, boundary forms, and known regressions.
- Add token dictionaries only for syntax that unlocks deeper states.
- Combine compatible sanitizers and compiler instrumentation deliberately.
- Preserve crashing inputs and tool metadata in a bounded, non-secret artifact location.

## Run and Triage

- Start with a bounded smoke campaign before longer local or CI campaigns.
- Track executions, coverage growth, corpus size, timeouts, and unique signatures.
- Reproduce a crash outside the fuzzer with the exact artifact and build.
- Minimize the input, identify the first causal failure, and add a deterministic regression.
- Separate harness defects, resource exhaustion, duplicates, and product defects.
- Explain mutation, feedback, corpus evolution, and shrinking to the student using one observed case.

## Safety Boundaries

- Never fuzz production endpoints, privileged parsers, live credentials, or uncontrolled external services.
- Never execute generated programs or unfamiliar artifacts outside an appropriate sandbox.
- Bound CPU, memory, disk, process count, and wall time; stop before workspace stability is threatened.
- Do not claim security, completeness, or defect absence from campaign duration alone.

## Output Contract

- Report target, harness boundary, corpus, instrumentation, limits, and exact campaign command.
- Provide only observed crash signatures and coverage metrics; label campaigns not run.
- List minimized reproducers, fixes, regressions, and remaining high-risk surfaces.
