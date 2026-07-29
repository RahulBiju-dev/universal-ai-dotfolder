---
name: task-planner
description: "Convert an accepted software objective into ordered, dependency-aware implementation steps with acceptance gates and rollback points. Use when work spans multiple files, components, phases, owners, or validation stages and needs a concrete plan before edits begin."
---

# Task Planner
Turn a sufficiently defined objective into the smallest complete, verifiable execution sequence.

## Workflow
1. Inspect workspace instructions, repository state, relevant code, configuration, and tests.
2. Restate the observable goal, in-scope surfaces, exclusions, and completion criteria.
3. Identify invariants, public contracts, consumers, dependencies, and destructive transitions.
4. Split work into testable increments that leave the repository coherent after each step.
5. Mark dependency edges, safe parallel work, decision points, and required approvals.
6. Attach one acceptance check and, where state changes, one rollback path to every step.
7. Order cheap discovery and validation before expensive or irreversible operations.

## Decision Boundaries
- Use `prompt-upscaler` when the objective or output contract is still materially vague.
- Use `architecture-decision` when competing designs require an explicit tradeoff decision.
- Do not execute the plan, edit files, install dependencies, or mutate external systems unless requested.
- Do not invent owners, deadlines, interfaces, commands, or product requirements.
- Stop for clarification when alternatives change public behavior or irreversible state.

## Quality Gates
- Ensure every step produces an observable artifact or verified state transition.
- Cover implementation, tests, compatibility, resource safety, documentation, and cleanup where relevant.
- Surface algorithmic complexity, concurrency, migration, and failure-path risks early.
- Label proposed commands as unexecuted until their results are observed.
- Remove speculative steps that do not advance an acceptance criterion.

## Output Contract
- State the goal, scope, assumptions, and open decisions first.
- Provide a table with `Step`, `Depends on`, `Change`, `Check`, and `Rollback`.
- Separate parallelizable work from the critical path.
- Rank material risks and name the evidence needed to close each one.
- Distinguish inspected facts, recommendations, and unvalidated expectations.
