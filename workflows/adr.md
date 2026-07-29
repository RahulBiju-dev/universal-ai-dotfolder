---
name: adr
description: Preserve an architecture decision with context, options, and review triggers.
---

# ADR Trajectory

When `/adr` is invoked, preserve all trailing text as task input; otherwise use
the active decision evidence and request its status.

1. Read `../skills/adr-writer/SKILL.md`.
2. Inspect repository ADR conventions, context, considered options, constraints,
   evidence, consequences, and review conditions.
3. Record the decision without reopening analysis or inventing acceptance.
4. Write only when an ADR destination or mutation request is explicit.
5. Return status, decision, alternatives, consequences, and review triggers
   concisely.
