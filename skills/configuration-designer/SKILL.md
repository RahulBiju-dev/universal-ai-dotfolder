---
name: configuration-designer
description: Design and review application configuration with typed schemas, deterministic precedence, secure secret handling, validation, migration, and operable defaults. Use for config files, environment variables, command flags, feature settings, runtime profiles, reload behavior, or configuration regressions.
---

# Configuration Designer

## Discover the Surface

1. Inspect every configuration source, consumer, default, persistence path, and existing migration.
2. Define precedence among built-ins, files, environment, command flags, and remote sources.
3. Classify values as public, sensitive, immutable, restart-required, or safely reloadable.
4. Record supported versions, platform paths, and compatibility obligations.

## Design the Schema

- Use typed fields with explicit units, ranges, enums, and nullability.
- Reject unknown or malformed values when silent fallback would hide operator error.
- Choose conservative defaults that preserve established behavior.
- Keep secrets out of source control, logs, diagnostics, generated examples, and client bundles.
- Separate secret references from secret values and fail closed when required credentials are absent.
- Make file writes atomic and preserve the last known-good configuration on failure.
- Define migration, deprecation, rollback, and forward-compatibility behavior.
- For reloads, validate a complete candidate before one atomic state transition.

## Validate and Teach

- Test missing files, empty values, invalid types, boundary values, precedence conflicts, and old schemas.
- Test permissions, interrupted writes, partial reads, and reload failure when relevant.
- Explain the full resolution chain from source to typed runtime value.
- Show the student why parsing, validation, normalization, and application are distinct stages.
- State whether each default is a product decision, compatibility constraint, or safe implementation choice.

## Safety Boundaries

- Never print credentials, read unrelated secret stores, or overwrite user configuration without explicit authority.
- Never use configuration text as executable code or interpolate it into shell commands.
- Do not promise hot reload, compatibility, or recovery without verified implementation evidence.

## Output Contract

- Provide the schema, precedence, validation errors, migration behavior, and secret boundary.
- Report exact checks run and list unresolved deployment or platform assumptions.
