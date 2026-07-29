---
name: test
description: Invoke autonomous Python or C regression-harness generation and verification.
---

# Test Trajectory

When `/test` is invoked, resolve trailing text to one Python or C source file and
an optional output path.

1. Read `../skills/test-generator/SKILL.md`.
2. Inspect existing contracts and tests before generating anything.
3. Invoke `../skills/test-generator/build_tests.py` without overwrite mode.
4. Review inferred cases and add semantic oracles only when source contracts
   establish expected behavior.
5. Run syntax or compile validation, then the narrow relevant test suite.
6. Report the generated artifact, executed checks, failures, and coverage limits.

Preserve existing tests unless overwrite was explicitly requested.
