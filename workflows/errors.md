---
name: errors
description: Map error origins through propagation, cleanup, retry, and recovery.
---

# Error-Handling Trajectory

When `/errors` is invoked, preserve all trailing text as task input; otherwise
use the active failure path.

1. Read `../skills/error-handling/SKILL.md`.
2. Inspect origins, translations, callers, cleanup, retries, deadlines,
   cancellation, logging, and user outcomes.
3. Classify each failure and define bounded handling and recovery contracts.
4. Keep diagnosis read-only unless fixes are explicitly requested.
5. Return the error-flow map, defects, tests, evidence, and compatibility risk
   concisely without claiming unrun recovery.
