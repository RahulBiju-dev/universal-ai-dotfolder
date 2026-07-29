---
description: Map direct and transitive effects of a proposed technical change.
argument-hint: proposed change, target paths, consumers, and compatibility constraints
---

# Analyze Change Impact

Preserve all text following `/impact` as task input. When empty, use the current
diff or active proposal.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/change-impact-analyzer/SKILL.md`.
2. Inspect definitions, callers, consumers, tests, schemas, configuration,
   build, deployment, persistence, and generated edges.
3. Follow the skill's blast-radius classification, rollout analysis, decision
   boundaries, quality gates, and output contract.
4. Keep analysis read-only unless implementation is explicitly requested.

Return a concise impact matrix, ordered validation scope, rollout constraints,
and blind spots. Separate repository evidence from external-consumer inference
and never claim complete coverage without proof.
