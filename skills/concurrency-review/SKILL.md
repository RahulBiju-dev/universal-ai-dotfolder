---
name: concurrency-review
description: Review concurrent code for data races, deadlocks, atomicity violations, unsafe publication, starvation, cancellation bugs, and lifecycle errors. Use for threads, async tasks, locks, atomics, channels, event loops, worker pools, or reports of timing-dependent and intermittent failures.
---

# Concurrency Review

## Build the Model

1. Inspect thread creation, task ownership, shared state, synchronization primitives, shutdown, and nearby tests.
2. List each mutable resource with its owner, allowed readers and writers, and protecting mechanism.
3. Draw the relevant happens-before edges and lock-order graph.
4. Identify progress requirements: blocking, lock-free, wait-free, fairness, backpressure, and cancellation.
5. Define the smallest observable failure schedule before proposing a fix.

## Audit Interleavings

- Check compound operations for lost updates, check-then-act races, and torn invariants.
- Check publication, memory ordering, condition-variable predicates, spurious wakeups, and missed notifications.
- Check lock ordering, reentrancy, callbacks under locks, priority inversion, and blocking while holding locks.
- Check task, thread, future, and channel lifetime across failure, timeout, cancellation, and shutdown.
- Check boundedness of queues, worker creation, retries, and pending work.
- Prefer ownership transfer, immutability, structured concurrency, or narrow critical sections over added global locks.
- Preserve deterministic ordering when output feeds tests, caches, or protocols.

## Verify and Teach

- Add a deterministic regression test or controlled scheduler seam when practical.
- Use existing race detectors, thread sanitizers, stress tests, or model checkers only when configured and authorized.
- Repeat timing-sensitive checks enough to gather evidence, but never convert nondetection into a safety claim.
- Explain the failing interleaving step by step and name the invariant it violates.
- Contrast mutual exclusion, visibility, atomicity, and progress so the student learns the actual guarantee.
- State contention and throughput costs introduced by the fix.

## Safety Boundaries

- Avoid unbounded stress, production traffic, external services, and destructive fault injection.
- Do not change synchronization semantics merely to silence a detector.
- Do not infer thread safety from API names, single runs, or the absence of warnings.

## Output Contract

- Rank findings by reproducibility and consequence.
- Include shared state, failing schedule, violated invariant, minimal remedy, and validation evidence.
- Mark suspected races, platform-dependent behavior, and checks not run explicitly.
