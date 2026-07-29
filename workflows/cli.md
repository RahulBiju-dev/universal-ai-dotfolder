---
name: cli
description: Design a stable command grammar with composable output and precise errors.
---

# CLI Trajectory

When `/cli` is invoked, preserve all trailing text as task input; otherwise use
the active command-interface request.

1. Read `../skills/cli-designer/SKILL.md`.
2. Inspect grammar, help, parsers, defaults, exit codes, stdout and stderr,
   configuration, scripts, tests, and compatibility.
3. Define predictable interactive and non-interactive behavior.
4. Edit only when implementation is requested; otherwise return the interface
   contract.
5. Return commands, flags, errors, examples, compatibility, and validation
   evidence concisely without fabricating output.
