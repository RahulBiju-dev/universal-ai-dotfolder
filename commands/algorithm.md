---
description: Design a correct algorithm from explicit constraints, invariants, and bounds.
argument-hint: problem statement, input limits, required output, and performance target
---

# Design Algorithm

Preserve all text following `/algorithm` as task input. When empty, ask for the
problem statement and input constraints.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/algorithm-designer/SKILL.md`.
2. Inspect existing code or examples, formalize inputs and outputs, and compare
   candidate structures and methods.
3. Follow the skill's correctness proof, complexity analysis, adversarial tests,
   decision boundaries, and output contract.
4. Write code only when implementation is explicitly requested.

Return the chosen algorithm, invariant or proof sketch, time-space bounds,
tradeoffs, and test cases concisely. Label expected or amortized claims and
never present an unchecked example as proof.
