---
name: bench
description: Produce a reproducible benchmark with controlled samples and thresholds.
---

# Benchmark Trajectory

When `/bench` is invoked, preserve all trailing text as task input; otherwise
request the workload and decision the benchmark must support.

1. Read `../skills/benchmark-harness/SKILL.md`.
2. Inspect correctness oracles, input distributions, setup, warmup, isolation,
   existing benchmarks, environment, and noise.
3. Define sampling, statistics, comparison, and regression thresholds.
4. Default to read-only design; create or execute only when explicitly requested.
5. Return methodology, harness, samples, variance, comparison, and limitations
   concisely without claiming unmeasured performance.
