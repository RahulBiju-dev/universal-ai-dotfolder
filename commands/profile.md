---
description: Measure and attribute a reproducible CPU, memory, I/O, or latency bottleneck.
argument-hint: target, workload, metric, baseline, environment, and profiler constraints
---

# Profile Performance

Preserve all text following `/profile` as task input. When empty, request the
target workload and user-visible metric.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/performance-profiler/SKILL.md`.
2. Inspect correctness checks, build mode, workload, complexity, prior
   measurements, environment, and available profiling tools.
3. Follow the skill's baseline, sampling, attribution, decision boundaries,
   quality gates, and output contract.
4. Do not edit source unless optimization is requested; ask before privileged,
   installed, or costly profiling.

Report method, baseline, variance, hotspots, confidence, and next experiment
concisely. Distinguish measurements from projections and never fabricate
profiler output or improvement.
