---
name: invariant-miner
description: "Derive candidate preconditions, postconditions, state, loop, data, ownership, and concurrency invariants from code, tests, specifications, and traces. Use when legacy behavior is unclear, assertions or property tests are needed, or a refactor requires explicit contracts without pretending observed patterns are guarantees."
---

# Invariant Miner
Extract candidate truths from evidence and classify how strongly each one is supported.

## Workflow
1. Inspect the narrow target, callers, state transitions, tests, specifications, and available traces.
2. Identify boundaries where data, ownership, authority, or lifecycle state changes.
3. Propose candidate preconditions, postconditions, representation, loop, and temporal invariants.
4. Trace each candidate to source evidence and search for contradicting paths or fixtures.
5. Classify it as proven, contract-stated, repeatedly observed, hypothesized, or contradicted.
6. Construct a minimal counterexample attempt and identify missing input or concurrency dimensions.
7. Translate supported candidates into assertions, types, property tests, or documentation recommendations.

## Decision Boundaries
- Use `code-explainer` when the goal is understanding flow rather than extracting contracts.
- Use `algorithm-designer` to establish invariants for a new solution.
- Do not promote naming, one trace, current tests, or common behavior into a guarantee.
- Do not execute untrusted code or collect production traces without explicit authorization.
- Preserve contradictory evidence instead of forcing a single coherent story.

## Quality Gates
- Scope every invariant to a function, type, state, phase, or concurrency domain.
- State quantifiers, validity windows, ownership, and exceptional states precisely.
- Check empty, maximum, malformed, reentrant, partial-failure, and cancellation paths.
- Surface architectural coupling and complexity assumptions embedded in the candidate.
- Never label an invariant proven without a proof or exhaustive finite argument.

## Output Contract
- Provide `Candidate invariant`, `Scope`, `Class`, `Evidence`, `Counterexample`, and `Check`.
- Lead with contradicted or safety-critical candidates.
- Separate source contracts, observed regularities, and hypotheses.
- Recommend the narrowest assertion or test that can validate each candidate.
- List unresolved paths, missing evidence, and any execution not performed.
