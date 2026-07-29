---
name: mutation-tester
description: Evaluate test-suite fault detection with bounded mutation testing and translate surviving mutants into stronger behavioral assertions. Use for mutation scores, weak tests, equivalent-mutant triage, test quality audits, or targeted validation of critical modules.
---

# Mutation Tester

## Prepare the Experiment

1. Require a deterministic green baseline and inspect existing test duration, coverage, and mutation tooling.
2. Select a small high-risk module, relevant tests, operator set, timeout, and resource budget.
3. Exclude generated, vendored, trivial, and unsupported code with explicit reasons.
4. Preserve the original source and isolate mutation artifacts from the working tree.

## Run and Classify

- Start with a smoke sample before expanding the mutation set.
- Run mutants independently and distinguish killed, survived, timed out, invalid, uncovered, and tool-error outcomes.
- Inspect surviving mutants against the public contract before adding a test.
- Classify semantically equivalent mutants separately and justify equivalence precisely.
- Treat timeout changes as potential performance or termination defects, not automatic kills.
- Prefer tests that catch a behavior class over assertions tailored to one textual mutation.

## Improve and Teach

- Add focused assertions for boundary conditions, error handling, state transitions, and returned effects.
- Re-run the affected mutant and nearby suite after each test change.
- Explain to the student how mutation testing evaluates oracle strength rather than implementation coverage alone.
- Show one surviving mutant, the missing contract assertion, and the strengthened test.
- Track score only within a stable scope and do not optimize it as an isolated target.

## Safety Boundaries

- Never mutate production artifacts, user changes, generated outputs, or an uncommitted working tree in place.
- Do not install tooling or launch an expensive full-repository campaign without approval.
- Bound process count, time, memory, and stored logs.
- Never claim test adequacy solely from a mutation score.

## Output Contract

- Report baseline, scope, operators, budget, outcome counts, and surviving high-value mutants.
- List tests added, exact reruns, equivalent-mutant rationale, tool failures, and untested scope.
