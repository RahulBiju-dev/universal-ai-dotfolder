---
name: coverage
description: Measure coverage dimensions and rank risky unexercised behavior.
---

# Coverage Trajectory

When `/coverage` is invoked, preserve all trailing text as task input; otherwise
use existing coverage configuration or request a test command.

1. Read `../skills/coverage-analyzer/SKILL.md`.
2. Inspect tests, instrumentation, exclusions, generated code, source maps,
   prior reports, changed code, and risk boundaries.
3. Run only authorized coverage collection and verify report provenance.
4. Keep source and tests unchanged unless additions are requested; ask before
   installing tools.
5. Return commands, dimensions, risky gaps, instrumentation limits, and next
   tests concisely without equating percentage with correctness.
