---
description: Inspect an active Python or C target and generate missing boundary and regression tests.
argument-hint: source file and optional output path
---

# Build Tests

Treat the text following `/test` as the source target and optional destination;
when empty, use the active source file.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/test-generator/SKILL.md`.
2. Inspect existing tests, interfaces, contracts, and prior regressions.
3. Run the sibling skill's `build_tests.py` without force.
4. Review the generated harness and add semantic assertions only when the
   contract proves the expected result.
5. Run syntax checks and the narrowest project-native test command.

Cover success, empty input, boundaries, malformed data, timeout or failure
paths, and the reported regression where defensible. Never overwrite an
existing test without explicit authorization. Report generated paths, executed
checks, coverage limits, and failures.
