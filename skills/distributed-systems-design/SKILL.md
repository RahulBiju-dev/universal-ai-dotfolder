---
name: distributed-systems-design
description: Design and critique distributed services through explicit failure models, consistency guarantees, data ownership, idempotency, scalability, and operability. Use for service boundaries, replication, queues, consensus, caching, sharding, retries, multi-region systems, or architecture tradeoff analysis.
---

# Distributed Systems Design

## Frame the System

1. Establish actors, trust boundaries, data ownership, request paths, and expected load.
2. Define latency, throughput, durability, availability, consistency, recovery, and cost objectives.
3. State the failure model for process crashes, partitions, delayed or duplicated messages, clock skew, and dependency loss.
4. Separate required guarantees from preferences and locally reversible implementation choices.

## Design the Protocol

- Assign one authoritative owner for each invariant and state transition.
- Define identifiers, ordering, idempotency keys, deduplication windows, and retry budgets.
- Choose consistency per operation; describe stale reads, conflicts, and convergence explicitly.
- Bound queues, fan-out, replication lag, retention, cache staleness, and recovery work.
- Design timeouts, backoff with jitter, circuit breaking, backpressure, and load shedding together.
- Specify schema evolution, rolling compatibility, replay behavior, and disaster recovery.
- Keep authentication, authorization, encryption, tenant isolation, and auditability at every boundary.
- Add observability for request identity, saturation, retries, correctness signals, and recovery progress.

## Challenge the Design

- Walk normal, degraded, partitioned, overloaded, and recovery sequences.
- Test duplicate, reordered, lost, delayed, and poison messages.
- Identify split-brain paths, cascading failures, hot keys, thundering herds, and retry amplification.
- Estimate bottlenecks and state time and space complexity for routing or coordination algorithms.
- Prefer the simplest architecture that meets quantified requirements.

## Teach the Tradeoffs

- Explain which guarantee each mechanism provides and which it cannot provide.
- Use one concrete timeline to distinguish consistency, availability, durability, and exactly-once effects.
- Give the student a falsifiable question for every major design assumption.

## Safety Boundaries

- Never mutate cloud resources, production data, DNS, credentials, or deployment state without explicit approval.
- Never claim fault tolerance, scale, or service-level compliance without executed evidence.
- Label estimates and assumptions separately from measured behavior.

## Output Contract

- Provide the architecture, invariants, failure handling, capacity assumptions, and key alternatives.
- Record rejected options with concise tradeoffs and list validation or simulation still required.
