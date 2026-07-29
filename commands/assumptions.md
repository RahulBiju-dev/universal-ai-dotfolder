---
description: Extract and challenge hidden assumptions that could invalidate proposed work.
argument-hint: requirements, plan, estimate, design, or technical claim
---

# Audit Assumptions

Preserve all text following `/assumptions` as task input. When empty, analyze the
active requirements or plan.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/assumption-auditor/SKILL.md`.
2. Inspect relevant contracts, environments, scale, ownership, compatibility,
   and validation evidence.
3. Follow the skill's classification, challenge, decision boundaries, quality
   gates, and output contract.
4. Keep the audit read-only and do not silently resolve material unknowns.

Report the assumption register, evidence, failure consequence, verification
method, and decision owner concisely. Do not present inference as fact or claim
checks that did not run.
