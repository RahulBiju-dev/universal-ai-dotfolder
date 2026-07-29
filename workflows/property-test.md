---
name: property-test
description: Define invariants, generators, shrinking, and reproducible property oracles.
---

# Property-Test Trajectory

When `/property-test` is invoked, preserve all trailing text as task input;
otherwise request the target contract and intended invariant.

1. Read `../skills/property-test-designer/SKILL.md`.
2. Inspect data domains, state transitions, invalid inputs, existing tests,
   framework conventions, and oracle options.
3. Define independent properties, constrained generators, shrinkers, and seeds.
4. Default to read-only design; write tests only when generation is requested.
5. Return properties, domains, shrink strategy, and evidence concisely without
   promoting observed patterns to guarantees.
