---
description: Design high-value property tests with constrained generators and shrinking.
argument-hint: target interface, invariants, data domain, framework, and output path
---

# Design Property Tests

Preserve all text following `/property-test` as task input. When empty, use the
active deterministic interface and ask for its invariant.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/property-test-designer/SKILL.md`.
2. Inspect contracts, examples, state transitions, invalid domains, existing
   tests, framework conventions, seeds, and oracle options.
3. Follow the skill's invariant, generator, shrinker, decision boundaries,
   quality gates, and output contract.
4. Default to read-only design; write tests only when generation is explicitly
   requested and never overwrite existing files silently.

Report properties, generators, constraints, shrink strategy, seeds, and oracle
evidence concisely. Never label observed patterns as guaranteed invariants.
