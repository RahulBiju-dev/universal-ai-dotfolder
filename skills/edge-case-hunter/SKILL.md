---
name: edge-case-hunter
description: Analyze implementation and interface boundaries for missing edge cases, hidden-test failures, malformed inputs, numerical limits, partial operations, concurrency hazards, and recovery gaps. Use for robustness reviews, boundary-case inventories, adversarial test planning, or pre-merge edge-case analysis.
---

# Edge Case Hunter

Derive concrete failure cases from contracts and control flow before suggesting changes.

## Workflow

1. Establish the target interface, intended behavior, input domain, state model, and scale limits.
2. Inspect callers, callees, validation, cleanup, tests, and external contracts before enumerating cases.
3. Partition cases into empty, singleton, minimum, maximum, malformed, duplicate, reordered, and cyclic inputs.
4. Trace partial reads, writes, initialization, cancellation, timeout, retry, dependency failure, and recovery.
5. Check arithmetic overflow, precision loss, encoding, platform width, resource exhaustion, and adversarial complexity.
6. Check shared-state interleavings, reentrancy, repeated invocation, idempotency, and shutdown races where relevant.
7. Rank only reachable cases by impact, likelihood, detectability, and current coverage.

## Decision Boundaries

- Keep analysis read-only unless the user explicitly requests fixes or tests.
- Treat documented preconditions as boundaries, then verify that callers uphold them.
- Exclude impossible cases only with code, type, protocol, or invariant evidence.
- Distinguish observed failures, code-proven risks, and speculative stress scenarios.
- Use `skills/repo-search/search.py` only when the target surface is not already known.

## Quality Gates

- Tie every reported case to a concrete interface, branch, state, or resource transition.
- State the exact trigger and expected safe behavior for each case.
- Avoid duplicating equivalent cases under different names.
- Cover success, rejection, cleanup, and post-failure usability.
- Never claim a case is handled or a test passes unless validation actually ran.

## Output Contract

- Return a severity-ranked table with trigger, affected path, expected behavior, evidence, and coverage.
- Separate confirmed gaps from inferred risks.
- Identify the smallest useful regression test for each actionable gap.
- Report inspected files, validation performed, execution limits, and residual uncertainty.
