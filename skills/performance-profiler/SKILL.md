---
name: performance-profiler
description: Measure and diagnose CPU, allocation, memory, I/O, latency, throughput, contention, startup, or binary-size bottlenecks using reproducible workloads. Use for slow code, regressions, scaling limits, resource spikes, profiler interpretation, or evidence before optimization.
---

# Performance Profiler

Measure the right workload before attributing cost or recommending optimization.

## Workflow

1. Define the user-visible metric, workload, input distribution, environment, and success threshold.
2. Establish correctness checks and a repeatable baseline before profiling.
3. Analyze expected time and space complexity to identify scale-sensitive candidates.
4. Select the narrowest profiler or measurement method for CPU, memory, I/O, locks, or latency.
5. Capture multiple comparable samples with warmup, variance, and environmental noise recorded.
6. Attribute dominant cost to concrete functions, allocations, waits, or system boundaries.
7. Re-measure after any explicitly requested optimization and compare against the same baseline.

## Decision Boundaries

- Keep profiling conclusions and recommendations read-only unless optimization is explicitly requested.
- Ask before installing profilers, using privileged counters, or running costly workloads.
- Do not extrapolate microbenchmarks directly to production behavior.
- Separate algorithmic limits, implementation cost, dependency cost, and measurement artifacts.
- Use `skills/shell-exec/exec.py` for bounded authorized local profiling commands.

## Quality Gates

- Preserve workload, build mode, versions, hardware context, and profiler configuration.
- Report sample count, central tendency, spread, and meaningful uncertainty.
- Confirm that instrumentation overhead does not dominate the result.
- Pair performance comparisons with correctness validation.
- Never claim an improvement or bottleneck without measured evidence.

## Output Contract

- Report workload, environment, baseline, method, hotspot evidence, and variance.
- Rank opportunities by expected impact, confidence, effort, and correctness risk.
- Distinguish measurements from projections and hypotheses.
- State unmeasured dimensions, scaling limits, and the next discriminating experiment.
