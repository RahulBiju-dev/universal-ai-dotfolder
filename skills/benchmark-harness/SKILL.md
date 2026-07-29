---
name: benchmark-harness
description: Design and implement reproducible performance benchmarks with controlled inputs, warmup, sampling, statistical summaries, and regression thresholds. Use for algorithm comparisons, latency or throughput measurement, memory benchmarks, optimization claims, or performance CI gates.
---

# Benchmark Harness

## Define the Claim

1. State the operation, metric, input distribution, scale, baseline, and practical decision the benchmark supports.
2. Separate setup, measured work, teardown, and validation of the result.
3. Identify compiler, runtime, hardware, power, affinity, load, and dependency factors that can bias results.
4. Choose latency, throughput, allocation, peak memory, or another metric tied to user impact.

## Build the Harness

- Generate deterministic representative, boundary, and adversarial inputs.
- Prevent dead-code elimination and verify every measured operation produces a correct result.
- Warm up runtimes and caches when appropriate, then collect multiple independent samples.
- Randomize or alternate candidate order when drift could favor one implementation.
- Keep measurement overhead small and quantify it when material.
- Bound sample duration, memory, output, and dataset size.
- Record raw observations and environment metadata before summarizing.

## Analyze and Teach

- Report robust summaries, dispersion, sample count, and units.
- Treat small differences within noise as inconclusive.
- Compare like-for-like builds and include algorithmic behavior across multiple input sizes.
- Explain asymptotic complexity separately from constant factors and measured crossover points.
- Teach the student why a faster microbenchmark may not improve the full workload.
- Re-run surprising results and inspect profiles before attributing cause.

## Safety Boundaries

- Never benchmark production services, consume unbounded resources, alter system tuning, or pin privileged settings without approval.
- Never fabricate measurements or compare results from materially different environments as equivalent.
- Do not add a CI threshold until variance and representative hardware are understood.

## Output Contract

- Provide the hypothesis, harness boundary, environment, inputs, samples, statistics, and raw-data location.
- State only measured conclusions; label noise, confounders, skipped environments, and follow-up profiling.
