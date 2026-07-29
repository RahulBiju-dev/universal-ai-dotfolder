---
name: shell-exec
description: Execute one local command as a direct argument vector with workspace-contained cwd, bounded runtime, process-group termination, concurrent output capture, truncation, and structured JSON state. Use for project tests, linters, builds, or diagnostics that do not require shell expansion.
---

# Shell Execution

1. Inspect the command, working directory, and side effects.
2. Resolve the skill directory as the directory containing this file.
3. Pass an argument vector after `--`:

   ```text
   python3 exec.py --root WORKSPACE --cwd WORKSPACE -- executable argument
   ```

4. Read `status`, `exit_code`, `signal`, `duration_ms`, and both bounded streams.
5. Report failures and truncation; never imply hidden output was inspected.

Shell syntax, pipes, redirects, substitutions, and chaining are passed literally.
Request confirmation before destructive, privileged, network-mutating, or
external actions. Never use this utility to bypass host permissions, execute
untrusted code as a sandbox, or print secrets. The workspace boundary constrains
only `cwd`; the child retains the user's ordinary filesystem and network access.
