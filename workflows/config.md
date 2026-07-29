---
name: config
description: Design typed configuration with deterministic precedence and safe secrets.
---

# Configuration Trajectory

When `/config` is invoked, preserve all trailing text as task input; otherwise
use the active settings problem.

1. Read `../skills/configuration-designer/SKILL.md`.
2. Inspect schemas, defaults, files, environment, flags, secrets, precedence,
   validation, reload, migration, and tests.
3. Specify deterministic resolution and safe failure behavior.
4. Keep review read-only unless implementation is requested; never expose or
   mutate live secrets.
5. Return schema, precedence, errors, migration, security boundaries, and
   evidence concisely.
