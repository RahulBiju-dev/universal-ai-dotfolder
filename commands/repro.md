---
description: Reduce a failure to a minimal deterministic and self-contained reproduction.
argument-hint: symptom, original target, inputs, environment, and reproduction constraints
---

# Build Reproducer

Preserve all text following `/repro` as task input. When empty, request the
symptom, source case, and expected behavior.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/reproducer-builder/SKILL.md`.
2. Inspect the original inputs, environment, dependencies, timing, side effects,
   logs, and smallest relevant execution path.
3. Follow the skill's reduction, determinism, isolation, decision boundaries,
   quality gates, and output contract.
4. Create artifacts only when requested and inside an approved path; never copy
   secrets or mutate external systems.

Report the minimal case, exact setup and command, observed result, reduction
evidence, and remaining variability concisely. Never claim reproducibility
without repeated execution.
