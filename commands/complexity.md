---
description: Teach and derive rigorous time and space bounds for code or algorithms.
argument-hint: code, algorithm, input constraints, and target scale
---

# Analyze Complexity

Preserve all text following `/complexity` as task input. When empty, use the
active algorithm or selected code.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/complexity-coach/SKILL.md`.
2. Inspect loop bounds, recursion, data structures, amortization, allocation,
   hidden library work, and input distributions.
3. Follow the skill's derivation, teaching, comparison, quality gates, and
   output contract.
4. Keep the analysis read-only unless optimization is explicitly requested.

Return the derivation, tightest defensible bounds, dominant terms, assumptions,
and alternatives concisely. Distinguish worst-case, expected, amortized, and
measured behavior; never assert an unproved bound.
