---
name: algorithm-designer
description: "Design a correct algorithm and supporting data structures from explicit input constraints, invariants, and performance targets. Use for graph, search, optimization, dynamic programming, streaming, scheduling, or interview problems that need option comparison, proof, complexity, and adversarial tests."
---

# Algorithm Designer
Derive the simplest correct algorithm that meets the stated time, space, and implementation constraints.

## Workflow
1. Formalize inputs, outputs, invalid states, equivalence, scale, and determinism requirements.
2. Derive invariants and lower-bound intuition before selecting a familiar pattern.
3. Generate a small set of viable approaches and identify the condition each exploits.
4. Compare worst-case time, auxiliary space, output cost, stability, and implementation risk.
5. Choose one approach and state its preconditions, state representation, and transitions.
6. Prove initialization, preservation, progress or termination, and postcondition in a compact sketch.
7. Validate against empty, minimal, maximal, duplicate, cyclic, disconnected, and adversarial inputs.

## Decision Boundaries
- Use `complexity-coach` when the primary goal is learning to derive a bound.
- Do not optimize without input scale or a constraint that rejects the simpler method.
- Do not call a heuristic optimal or a randomized bound deterministic.
- Do not assume arithmetic is unbounded; address overflow, precision, and sentinel values.
- Implement code only when requested and preserve the target language's safety conventions.

## Quality Gates
- Define every complexity variable and distinguish expected, amortized, and worst-case claims.
- Make tie-breaking and iteration order deterministic when outputs feed tests or caches.
- Check the proof against the actual pseudocode rather than an idealized variant.
- Include a brute-force oracle or independently checkable property for small inputs where practical.
- State memory layout, recursion depth, and mutation costs when they affect feasibility.

## Output Contract
- State the formal problem, constraints, and chosen invariant.
- Provide a candidate comparison table and decisive tradeoff.
- Give language-neutral pseudocode with explicit failure behavior.
- Include the proof sketch, time and space bounds, and their assumptions.
- Provide a compact adversarial test set and unresolved limitations.
