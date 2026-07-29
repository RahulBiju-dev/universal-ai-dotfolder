---
name: cli-designer
description: Design and implement stable command-line interfaces with composable output, precise errors, safe defaults, and backward-compatible command grammars. Use for new CLIs, subcommands, flags, help text, exit codes, interactive prompts, scripting behavior, or command-interface reviews.
---

# CLI Designer

## Define the Contract

1. Inspect the existing parser, command hierarchy, configuration, output conventions, and tests.
2. Identify human, script, CI, and machine-readable consumers.
3. Specify command grammar, defaults, precedence, exit codes, stdout, stderr, and side effects.
4. Preserve existing invocations unless a breaking change is explicit and migration is defined.

## Design and Implement

- Use predictable verb-noun commands and consistent flag names.
- Make required inputs explicit; avoid positional ambiguity and surprising environment dependence.
- Reserve stdout for requested data and stderr for diagnostics.
- Provide stable structured output only through an explicit format flag.
- Make `--help` useful without execution and make `--version` deterministic.
- Require confirmation for destructive interactive actions and an explicit opt-in for noninteractive use.
- Detect non-TTY input; never hang CI waiting for a prompt.
- Handle signals, cancellation, partial output, broken pipes, and cleanup.
- Redact secrets from arguments, errors, traces, history guidance, and generated examples.

## Validate and Teach

- Test success, invalid syntax, missing inputs, boundary values, conflicting flags, and dependency failure.
- Test exit status and both output streams, not only rendered text.
- Test shell completion or structured output only when the project supports it.
- Explain how parsing, validation, execution, and presentation remain separate and testable.
- Show the student how one command behaves in both a terminal and a pipeline.

## Safety Boundaries

- Never execute destructive examples, install completion files, or modify user configuration without approval.
- Avoid shell interpolation and pass untrusted values as argument-vector elements.
- Never claim portability across shells or platforms that were not checked.

## Output Contract

- Report the command contract, compatibility impact, safety behavior, and examples exercised.
- Include exact tests run and label unverified shells, platforms, and integrations.
