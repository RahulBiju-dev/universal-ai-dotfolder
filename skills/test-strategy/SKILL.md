---
name: test-strategy
description: "Design a risk-based test strategy across unit, integration, contract, property, fuzz, concurrency, fault, and system layers. Use before implementation, release, or regression repair when behaviors, failure modes, or coverage priorities need an explicit and efficient verification plan."
---

# Test Strategy
Allocate test effort to the failures most likely to violate important contracts.

## Workflow
1. Inspect requirements, architecture, changed paths, interfaces, existing tests, and prior failures.
2. Convert observable contracts and invariants into a risk-ranked behavior matrix.
3. Select the narrowest stable layer that can prove each behavior without duplicating coverage.
4. Define deterministic examples, boundary partitions, malformed inputs, and regression cases.
5. Add properties, fuzz targets, schedule variation, fault injection, or system tests where risk justifies them.
6. Specify fixtures, isolation, clocks, randomness, external dependencies, and cleanup.
7. Order a fast local signal before broader integration and release gates.

## Decision Boundaries
- Use `test-generator` for a Python or C smoke harness after the strategy identifies a target.
- Do not generate test code unless requested and do not weaken assertions to fit current behavior.
- Do not equate line coverage with behavioral confidence.
- Do not claim exhaustive testing, race freedom, or production equivalence.
- Avoid expensive end-to-end tests when a lower layer proves the same invariant.

## Quality Gates
- Cover success, empty, boundary, malformed, timeout, dependency failure, and recovery paths.
- Include old-client, new-client, migration, or rollback states for evolving contracts.
- Require a clear oracle and make nondeterminism controllable or observable.
- Confirm every proposed test can fail for its intended regression.
- Balance confidence against runtime, maintenance cost, and diagnostic precision.

## Output Contract
- State scope, critical invariants, and the dominant risk model.
- Provide `Risk`, `Behavior`, `Layer`, `Oracle`, `Fixture`, and `Priority` columns.
- Separate mandatory release gates from optional depth tests.
- List required tooling, data, environments, and execution limits.
- Mark existing evidence, planned tests, and unverified coverage distinctly.
