---
name: reproducer-builder
description: Build minimal, deterministic, self-contained reproductions for crashes, incorrect output, races, hangs, performance regressions, and integration failures. Use when a bug report is intermittent, environment-dependent, noisy, too large, or missing an executable regression case.
---

# Reproducer Builder

## Capture the Failure

1. Record exact observed behavior, expected behavior, input, command, exit status, environment, and frequency.
2. Preserve the original evidence read-only and separate facts from reporter inference.
3. Verify the failure before minimizing when execution is safe and authorized.
4. Define one deterministic oracle that distinguishes pass, fail, timeout, and setup error.

## Isolate and Minimize

- Remove unrelated services, files, flags, data, threads, and timing dependencies one variable at a time.
- Replace networks, clocks, randomness, and external state with controlled local fixtures.
- Minimize input structure while preserving validity rules relevant to the failure.
- Pin toolchain and dependency versions only as tightly as evidence requires.
- Bound runtime, memory, process count, output, retries, and temporary storage.
- Keep setup idempotent and cleanup reliable after success, failure, timeout, or cancellation.

## Convert to a Regression

- Re-run the minimal case from a clean state multiple times when intermittency matters.
- Verify the oracle fails before the fix and passes after it.
- Place the case at the narrowest test layer that still expresses public behavior.
- Preserve the minimized artifact when it adds information unavailable in code.
- Explain each removed variable and the remaining causal hypothesis to the student.
- Distinguish reproduction, localization, and root-cause proof.

## Safety Boundaries

- Redact credentials, personal data, private paths, raw environment dumps, and proprietary payloads.
- Never contact production, execute unfamiliar payloads, or reproduce destructive behavior without explicit approval and containment.
- Do not alter user data, global configuration, or unrelated repository state.
- Never claim reproduction when the exact failure was not observed.

## Output Contract

- Provide prerequisites, exact steps, minimal input, oracle, expected and actual results, and cleanup.
- Report reproduction count, environment, artifacts, and commands actually run.
- Label nondeterminism, unavailable dependencies, sanitization changes, and remaining hypotheses.
