---
description: Design or review typed configuration with deterministic precedence and safe defaults.
argument-hint: settings, sources, precedence, reload behavior, and migration needs
---

# Design Configuration

Preserve all text following `/config` as task input. When empty, use the active
configuration problem and existing files.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/configuration-designer/SKILL.md`.
2. Inspect schemas, defaults, files, environment variables, flags, secret
   handling, precedence, validation, reload, compatibility, and tests.
3. Follow the skill's configuration workflow, decision boundaries, quality
   gates, and output contract.
4. Keep review read-only unless implementation is requested; never expose live
   secrets or mutate external settings.

Return the schema, precedence, errors, migration, security boundaries, and
validation evidence concisely. Distinguish observed configuration behavior from
intended policy.
