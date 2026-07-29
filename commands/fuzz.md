---
description: Plan or implement bounded fuzzing for hostile and failure-prone input paths.
argument-hint: parser or interface, language, harness target, corpus, and execution budget
---

# Design Fuzzing

Preserve all text following `/fuzz` as task input. When empty, use the active
input boundary and request the target behavior.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/fuzzing-strategy/SKILL.md`.
2. Inspect parsing boundaries, invariants, existing harnesses, corpus, formats,
   sanitizers, determinism, side effects, and crash handling.
3. Follow the skill's harness, corpus, budget, triage, decision boundaries,
   quality gates, and output contract.
4. Default to a read-only strategy; create or execute fuzzing only when
   explicitly requested and safe.

Report targets, oracle, corpus, dictionary, resource limits, triage, and
coverage evidence concisely. Never claim fuzz coverage or safety from an unrun
campaign.
