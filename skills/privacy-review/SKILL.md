---
name: privacy-review
description: Review personal or sensitive data collection, purpose, flow, storage, sharing, retention, deletion, access, logging, and user control. Use for feature design, telemetry, AI data use, third-party integrations, privacy-impact analysis, minimization, consent flows, or data-lifecycle changes.
---

# Privacy Review

Trace data through its full lifecycle and minimize exposure before proposing controls.

## Workflow

1. Define the feature, users, jurisdictions supplied by the user, and decision scope.
2. Inventory personal, sensitive, inferred, credential, content, and metadata fields.
3. Map collection sources, purposes, transformations, stores, processors, recipients, and access roles.
4. Trace retention, backups, caches, logs, model inputs, exports, deletion, and recovery copies.
5. Evaluate necessity, proportionality, defaults, transparency, user control, and purpose compatibility.
6. Identify reidentification, overcollection, secondary use, excessive retention, and third-party risks.
7. Recommend minimization and lifecycle controls with verifiable behavior.

## Decision Boundaries

- Keep review read-only unless implementation is explicitly requested.
- Do not provide definitive legal conclusions or invent jurisdictional requirements.
- Do not expose or copy real personal data during analysis.
- Separate repository evidence, product-policy assumptions, and questions for privacy or legal specialists.
- Use repository search only to locate concrete data fields, stores, logs, and outbound flows.

## Quality Gates

- Account for every identified sensitive field from collection through deletion.
- Verify that stated purpose matches actual processing and recipients.
- Include default behavior, opt-out or deletion paths, and failure handling.
- Treat logs, analytics, backups, prompts, embeddings, and support tooling as data stores.
- Never claim compliance, deletion, or minimization without evidence.

## Output Contract

- Return a data inventory and flow table with purpose, access, retention, deletion, and risk.
- Rank gaps by sensitivity, scale, exposure, user control, and reversibility.
- Provide technical controls and verification criteria without legal overclaiming.
- State assumptions, unresolved policy questions, and uninspected processors.
