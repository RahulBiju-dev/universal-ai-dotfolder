---
name: coverage-analyzer
description: Measure and interpret test coverage to find unexercised behavior, risky branches, and misleading instrumentation gaps. Use for line, branch, function, condition, or path coverage reports; changed-code coverage; test-suite audits; or coverage-gate design.
---

# Coverage Analyzer

## Establish the Scope

1. Inspect the test commands, instrumentation, generated code, exclusions, and baseline policy.
2. Choose line, branch, function, condition, or changed-code coverage based on the defect risk.
3. Define the source set and keep tests, vendors, generated files, and unreachable platform code classified explicitly.
4. Run the smallest authoritative suite that exercises the target before broader aggregation.

## Analyze the Report

- Verify source maps, compiler optimization, subprocess collection, and parallel-data merging.
- Locate uncovered error paths, boundaries, state transitions, cleanup, retries, and concurrency outcomes.
- Prioritize behavior whose failure consequence is high, not files with the lowest percentage alone.
- Inspect covered lines for weak assertions and branches reached without validating outcomes.
- Treat impossible or defensive branches through documented justification, not casual exclusion.
- Compare baseline and changed code using identical tooling and scope.

## Improve and Teach

- Add tests that assert contracts and externally observable behavior.
- Use focused examples for named regressions and properties or fuzzing for broad input spaces.
- Avoid tests that execute lines without detecting plausible faults.
- Explain statement reachability, branch decisions, oracle strength, and risk to the student.
- Show why complete line coverage cannot establish path completeness or correctness.

## Safety Boundaries

- Do not install coverage tooling, rewrite broad exclusions, or enforce a new gate without approval.
- Do not run destructive, external, privileged, or unbounded test suites.
- Never claim exhaustive testing or defect absence from a percentage.
- Report instrumentation failures rather than silently treating them as uncovered code.

## Output Contract

- Report scope, commands, tool version, metrics, high-risk gaps, and recommended tests.
- Separate observed coverage from inferred risk and label suites or platforms not run.
