---
name: requirement-griller
description: Resolve materially ambiguous software, product, architecture, or operational requests through a focused pre-implementation question gate. Use when missing decisions would change scope, public behavior, data handling, safety, cost, compatibility, acceptance criteria, or irreversible actions.
---

# Requirement Griller

## Preflight

1. Obey the root `AGENTS.md`, the user's explicit scope, and all higher-priority safety controls.
2. Inspect relevant source, tests, configuration, documentation, and repository state read-only.
3. Extract explicit requirements, constraints, exclusions, acceptance signals, and contradictions.
4. Separate locally discoverable facts and reversible defaults from decisions only the user can make.

## Question Gate

- Ask before implementation only when an unresolved choice materially changes the result or authority.
- Ask one to five high-leverage questions per round, ordered by dependency and decision impact.
- Map every question to one concrete decision; omit curiosity, ceremony, and repeated prompt content.
- Include one recommended default when it is safe, conventional, and reversible.
- Ask no question whose answer can be established reliably from the workspace.
- Use one round by default; follow up only when an answer creates a new material blocker.
- End the turn after asking questions; do not implement, mutate state, or perform external actions.

## Synthesis

1. Preserve every explicit answer and resolve contradictions openly.
2. Produce a compact contract with `Objective`, `Scope`, `Invariants`, `Acceptance`, `Validation`, and `Open Risks`.
3. Label unresolved assumptions and require another answer only when they remain material.
4. Resume the originally authorized work after resolution unless the user requested specification only.

## Guardrails

- Never invent product facts, credentials, permissions, deadlines, external systems, or user approval.
- Never broaden deliverables or weaken an explicit invariant to avoid asking a question.
- Prefer conventional reversible defaults for implementation details that do not alter observable behavior.
- Require explicit confirmation before destructive, privileged, credentialed, externally mutating, or irreversible action.
- Validate later claims with executed evidence and distinguish observed facts from projections.

## Output Contract

- Before resolution, output only the numbered questions with concise recommendations where useful.
- After resolution, state the compact contract once, then continue or hand it to the executing workflow.
- Report a blocker plainly when the user cannot supply authority or a required decision.
