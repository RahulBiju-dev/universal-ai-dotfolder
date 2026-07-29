---
description: Create or update concise technical documentation grounded in actual behavior.
argument-hint: documentation goal, audience, source paths, format, and destination
---

# Write Documentation

Preserve all text following `/docs` as task input. When empty, ask for the
audience, behavior, and target document.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/documentation-writer/SKILL.md`.
2. Inspect authoritative code, interfaces, commands, configuration, versions,
   tests, and existing documentation before drafting.
3. Follow the skill's task-oriented structure, decision boundaries, quality
   gates, and output contract.
4. Write only when the input requests a document or destination; otherwise
   return a read-only documentation plan.

Report changed documentation and verified commands, examples, links, and
limitations concisely. Never invent behavior, support, outputs, or successful
validation.
