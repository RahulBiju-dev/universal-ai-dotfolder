---
name: test-generator
description: Inspect one Python or C source file without importing or executing it and atomically generate a deterministic unittest regression harness. Use when interfaces lack tests, boundary and malformed-input smoke coverage is missing, or an active file needs a safe test scaffold.
---

# Test Generator

1. Inspect existing contracts and tests before generation.
2. Resolve the skill directory as the directory containing this file.
3. Run:

   ```text
   python3 build_tests.py --root WORKSPACE SOURCE
   ```

4. Review the reported inferred cases and limitations.
5. Add semantic assertions only when a contract establishes the expected result.
6. Run the generated harness with the project-native Python test runner.

The generator parses source statically and never overwrites by default. Use
`--force` only after explicit overwrite authorization. Generated boundary tests
isolate calls in subprocesses and can detect syntax, import, timeout, signal,
strict C compilation, and gross input-handling failures; they cannot infer
arbitrary semantic truth or prove exhaustive coverage.
