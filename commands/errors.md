---
description: Trace and harden error propagation, cleanup, retries, and recovery contracts.
argument-hint: failing path, error type, interface, symptom, or target module
---

# Design Error Handling

Preserve all text following `/errors` as task input. When empty, use the active
failure path or selected code.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/error-handling/SKILL.md`.
2. Inspect failure sources, translations, callers, cleanup, retries, timeouts,
   cancellation, fallbacks, logging, and user-visible outcomes.
3. Follow the skill's error-flow workflow, decision boundaries, quality gates,
   and output contract.
4. Keep diagnosis read-only unless fixes are explicitly requested.

Report origins, contracts, handling boundaries, cleanup, impact, and tests
concisely. Separate observed behavior from inferred paths and never claim
recovery works without validation.
