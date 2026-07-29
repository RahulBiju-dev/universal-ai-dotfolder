---
description: Record a proposed or accepted architecture decision without inventing consensus.
argument-hint: decision, status, evidence, options, consequences, and optional ADR path
---

# Write Architecture Decision Record

Preserve all text following `/adr` as task input. When empty, use the active
decision evidence and request its status.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/adr-writer/SKILL.md`.
2. Inspect existing ADR conventions, decision context, considered options,
   constraints, evidence, consequences, and review triggers.
3. Follow the skill's recording boundaries, quality gates, and output contract.
4. Create or edit an ADR only when a destination or write request is explicit;
   otherwise return the proposed record read-only.

Report status, decision, context, alternatives, consequences, and review
conditions concisely. Distinguish accepted facts from proposals and never
fabricate approval.
