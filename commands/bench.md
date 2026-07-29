---
description: Design or implement a reproducible benchmark with statistical comparison.
argument-hint: target, workload, metric, baseline, environment, and regression threshold
---

# Build Benchmark

Preserve all text following `/bench` as task input. When empty, request the
target workload and decision the benchmark must support.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/benchmark-harness/SKILL.md`.
2. Inspect correctness oracles, input distributions, setup cost, warmup,
   isolation, existing benchmarks, environment, and noise sources.
3. Follow the skill's harness design, sampling, statistics, decision boundaries,
   quality gates, and output contract.
4. Default to read-only design; create or execute benchmarks only when
   explicitly requested and bounded.

Report methodology, harness path, samples, variance, comparison, and limitations
concisely. Never claim a performance change from unrun or incomparable data.
