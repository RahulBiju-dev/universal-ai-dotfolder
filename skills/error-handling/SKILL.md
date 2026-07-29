---
name: error-handling
description: Analyze and improve error contracts, propagation, cleanup, retries, cancellation, fallbacks, and user-visible failure behavior. Use for swallowed exceptions, unchecked results, ambiguous errors, partial initialization, retry storms, resource leaks, or inconsistent failure handling across boundaries.
---

# Error Handling

Make failure behavior explicit, actionable, bounded, and safe across every exit path.

## Workflow

1. Identify failure sources, callers, trust boundaries, cleanup obligations, and user-visible outcomes.
2. Trace errors from origin through translation, logging, retry, recovery, and termination.
3. Classify failures as invalid input, transient dependency, permanent dependency, conflict, cancellation, or internal defect.
4. Define typed or structured contracts that preserve useful cause without leaking sensitive detail.
5. Pair every acquired resource and partial state with deterministic cleanup.
6. Bound retries with idempotency, backoff, jitter, deadlines, and terminal conditions.
7. Add focused tests for origin, propagation, cleanup, recovery, and post-failure usability.

## Decision Boundaries

- Keep diagnosis read-only unless the user explicitly requests fixes.
- Do not swallow, stringify indiscriminately, retry unknown failures, or convert defects into success.
- Preserve public error compatibility unless change is explicit.
- Separate operator diagnostics from safe user-facing messages.
- Use repository search only when error translation crosses unclear layers.

## Quality Gates

- Make ownership and cleanup valid on success, failure, timeout, and cancellation.
- Preserve causal context without duplicate noisy logging.
- Ensure recovery cannot corrupt state or repeat unsafe side effects.
- Define observable terminal behavior for every bounded retry loop.
- Never claim a failure path works unless it was inspected or executed.

## Output Contract

- Return an error-flow map with origin, contract, handling boundary, cleanup, and outcome.
- Rank defects by data loss, availability, security, and diagnosability impact.
- Provide changes and tests only when implementation is requested.
- State evidence, inferred behavior, untested paths, and compatibility risk.
