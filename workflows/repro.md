---
name: repro
description: Reduce a failure to a deterministic, minimal, self-contained reproducer.
---

# Reproducer Trajectory

When `/repro` is invoked, preserve all trailing text as task input; otherwise
request the symptom, source case, and expected behavior.

1. Read `../skills/reproducer-builder/SKILL.md`.
2. Inspect original inputs, environment, dependencies, timing, side effects,
   logs, and the smallest relevant path.
3. Remove one variable at a time while preserving the observed failure.
4. Create artifacts only in an explicit approved path and never copy secrets or
   mutate external systems.
5. Return the minimal case, setup, command, observed result, and variability
   concisely without claiming unrepeated reproduction.
