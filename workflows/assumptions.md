---
name: assumptions
description: Extract and rank hidden assumptions that threaten a plan or claim.
---

# Assumption Audit Trajectory

When `/assumptions` is invoked, preserve all trailing text as task input;
otherwise inspect the active requirements, plan, or design.

1. Read `../skills/assumption-auditor/SKILL.md`.
2. Inspect scale, behavior, environment, ownership, compatibility, and
   validation evidence.
3. Classify each assumption by evidence, consequence, reversibility, and owner.
4. Keep the audit read-only and leave material unknowns unresolved explicitly.
5. Return the assumption register, verification evidence, and verification
   order concisely without treating inference as fact.
