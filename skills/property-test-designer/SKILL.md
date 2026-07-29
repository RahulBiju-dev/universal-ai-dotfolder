---
name: property-test-designer
description: Design high-value property-based tests with precise invariants, constrained generators, shrinking, reproducible seeds, and useful failure oracles. Use for algorithms, parsers, serializers, state machines, numeric code, data structures, protocol transformations, or edge cases too broad for examples alone.
---

# Property Test Designer

## Derive Properties

1. Inspect the public contract, implementation, existing examples, and known failure classes.
2. Express invariants independently of the implementation under test.
3. Select properties such as round-trip, idempotence, monotonicity, conservation, equivalence, or model agreement.
4. Define valid, invalid, boundary, and adversarial input domains.
5. Keep example tests for named regressions and semantics properties cannot communicate clearly.

## Build Generators

- Generate structured values that satisfy domain constraints by construction.
- Bias deliberately toward empty, singleton, duplicate, maximum, degenerate, and malformed cases.
- Bound size, recursion, runtime, and allocation using expected production scale.
- Preserve relationships among dependent fields instead of filtering most generated cases.
- Define shrinkers that maintain validity and move toward a minimal explanatory failure.
- Use a simpler reference model when its independence and input limits are explicit.
- Capture seeds and minimized inputs for deterministic replay.

## Verify and Teach

- Run the cheapest property first and isolate global state, clocks, randomness, files, and networks.
- Confirm each property can fail by temporarily checking a known defect or a deliberately wrong local oracle when safe.
- Add every confirmed minimal counterexample as a focused regression when it carries durable meaning.
- Explain to the student why the property follows from the contract, not from current code.
- Distinguish generator coverage, logical strength, and execution count.

## Safety Boundaries

- Do not install a framework, generate unbounded data, call production services, or mutate external state without approval.
- Never weaken a property merely to make a failing implementation pass.
- Never claim exhaustiveness from randomized sampling.

## Output Contract

- List each property, generator domain, oracle, bounds, shrink behavior, and replay method.
- Report seeds, cases, runtime, failures, and exact commands only when observed.
- Label untested domains and weak or assumption-dependent oracles.
