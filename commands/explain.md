---
description: Explain concrete code through control flow, state, ownership, and contracts.
argument-hint: file, symbol, diff, or low-level construct plus learning goal
---

# Explain Code

Preserve all text following `/explain` as task input. When empty, use the active
selection or request a specific code target.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/code-explainer/SKILL.md`.
2. Inspect definitions, callers, data flow, state, ownership, errors, tests, and
   relevant platform semantics.
3. Follow the skill's audience calibration, decision boundaries, quality gates,
   and explanation contract.
4. Keep the route strictly read-only and separate explanation from review.

Report the layered explanation, concrete path evidence, invariants, and
complexity concisely. Mark inferred intent explicitly and never claim runtime
behavior that was not observed or proved.
