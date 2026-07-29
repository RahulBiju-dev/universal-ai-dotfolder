---
name: api-designer
description: "Design or evolve stable HTTP, RPC, event, or library API contracts with schemas, errors, compatibility, security, and operational behavior. Use when consumers need a new interface, an existing public contract must change, or endpoint semantics require decision-ready specification before implementation."
---

# API Designer
Define a consumer-centered contract that remains testable under failure, retries, and evolution.

## Workflow
1. Inspect existing conventions, consumers, domain invariants, trust boundaries, and version history.
2. Define actors, use cases, resources or operations, and explicit non-goals.
3. Specify requests, responses, events, validation, defaults, ordering, and error semantics.
4. Define authentication, authorization, idempotency, pagination, rate limits, and concurrency behavior.
5. Model timeout, retry, partial failure, duplicate delivery, and cancellation where applicable.
6. Compare compatibility-preserving options before proposing a breaking change.
7. Derive contract tests and one complete success and failure example.

## Decision Boundaries
- Do not invent domain fields, permissions, consumers, scale, or regulatory requirements.
- Use `database-designer` for storage modeling and keep persistence details out of public contracts.
- Use `architecture-decision` when transport or topology changes the system boundary materially.
- Preserve published behavior unless the user explicitly accepts migration and breakage.
- Do not implement or deploy the API unless requested.

## Quality Gates
- Make nullability, optionality, units, formats, limits, and version semantics explicit.
- Keep error codes stable, actionable, and free of secrets or internal stack details.
- Bound collections and state the complexity or payload impact of expensive operations.
- Check authorization at the resource and action level, not only authentication.
- Verify examples against the written schema and label unexecuted tests.

## Output Contract
- State consumers, use cases, invariants, and compatibility policy.
- Provide an operation table and concise request, response, and error schemas.
- Document retry, idempotency, pagination, concurrency, and lifecycle rules.
- List security controls, observability signals, and contract tests.
- Separate confirmed requirements, proposed choices, and unresolved decisions.
