---
name: ci-pipeline-builder
description: Design, implement, and review secure continuous-integration pipelines with deterministic checks, least privilege, effective caching, bounded matrices, and actionable failures. Use for GitHub Actions or other CI workflows, required checks, release gates, flaky jobs, cache issues, or pipeline performance.
---

# CI Pipeline Builder

## Inspect the Delivery Contract

1. Identify supported platforms, toolchains, artifacts, branch protections, release paths, and current checks.
2. Separate fast pull-request feedback from authoritative merge, nightly, and release validation.
3. Map credentials, permissions, untrusted inputs, third-party actions, caches, and artifact retention.
4. Establish failure ownership, expected duration, and mandatory versus advisory jobs.

## Build the Pipeline

- Use least-privilege job permissions and expose secrets only to the step that needs them.
- Pin external actions or images to immutable versions according to repository policy.
- Keep forked or untrusted code away from privileged tokens and deployment contexts.
- Order formatting, static checks, unit tests, integration tests, builds, and packaging by cost and signal.
- Bound matrices to supported combinations and explain every excluded case.
- Key caches from lockfiles, platform, toolchain, and relevant build inputs.
- Make artifacts deterministic, checksummed when distributed, and retained only as long as needed.
- Add timeouts, concurrency cancellation, retry limits, and concise failure logs.

## Validate and Teach

- Parse workflow syntax and run available local equivalents before claiming success.
- Exercise changed conditions, paths, matrix expressions, cache misses, and failure propagation.
- Explain to the student how trust boundaries differ for pull requests, protected branches, and releases.
- Show which evidence blocks a merge and which merely informs maintainers.
- Measure duration changes only from actual CI runs.

## Safety Boundaries

- Never push, enable workflows, change repository secrets, publish artifacts, or deploy without explicit authority.
- Never print tokens or use pull-request-controlled text in shell code.
- Do not remove a check solely to make the pipeline green.

## Output Contract

- Report jobs, triggers, permissions, dependencies, caches, artifacts, and required-check impact.
- List local validation performed and mark remote CI status or performance as unverified until observed.
