---
name: code-explainer
description: "Explain concrete source code through control flow, data flow, contracts, state, ownership, errors, and complexity. Use when a student must understand an unfamiliar function, module, subsystem, diff, or low-level construct before changing it, without turning the explanation into a code review."
---

# Code Explainer
Build an evidence-backed mental model of what the selected code does and why each part exists.

## Workflow
1. Inspect the exact target, its callers, callees, types, tests, and configuration needed for context.
2. Identify entry points, inputs, outputs, side effects, state, and external dependencies.
3. Trace one representative path in execution order using concrete names from the source.
4. Explain ownership, lifetimes, error propagation, concurrency, and cleanup where applicable.
5. Derive nontrivial time and space costs from the actual operations.
6. Relate syntax or patterns to their role only after explaining the surrounding behavior.
7. Confirm the model with a boundary case, test, or clearly labeled static inference.

## Decision Boundaries
- Use `code-griller` for defect-focused review; keep this skill descriptive unless critique is requested.
- Use `learning-tutor` for a broader curriculum or concept lesson beyond the selected code.
- Do not import, execute, or modify code merely to explain it.
- Do not infer runtime values, hidden contracts, or external behavior without evidence.
- Narrow the context when the requested depth does not require the whole repository.

## Quality Gates
- Cite file paths, symbols, and line references for material claims.
- Distinguish source-guaranteed behavior from naming conventions and likely intent.
- Explain state transitions and failure paths, not only the happy path.
- Surface architecture boundaries and complexity without inventing defects.
- Define jargon at first use and avoid restating obvious syntax line by line.

## Output Contract
- Start with a one-paragraph purpose and contract summary.
- Provide a numbered control-flow trace and a compact data or ownership map.
- List side effects, failure behavior, and complexity.
- Call out unknowns that require documentation, execution, or maintainer confirmation.
- End with two targeted comprehension checks when the user is learning.
