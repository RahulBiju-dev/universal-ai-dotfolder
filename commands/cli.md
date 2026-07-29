---
description: Design or implement a composable CLI with stable grammar and precise failures.
argument-hint: command goal, users, subcommands, flags, output, and compatibility
---

# Design CLI

Preserve all text following `/cli` as task input. When empty, use the active
command-interface request.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/cli-designer/SKILL.md`.
2. Inspect existing grammar, help, parsers, exit codes, stdout and stderr,
   configuration precedence, scripting use, tests, and compatibility.
3. Follow the skill's interface workflow, decision boundaries, quality gates,
   and output contract.
4. Edit only when implementation is requested; otherwise return a contract and
   examples.

Report grammar, defaults, errors, exit codes, machine-readable behavior,
compatibility, and validation concisely. Never fabricate command output or
claim shell portability without testing.
