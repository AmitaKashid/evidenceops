# ADR 0001: Use a bounded state graph for workflow orchestration

## Status
Accepted

## Context

The product must handle complex multi-step tasks while remaining inspectable, testable, and safe for business workflows. Free-form agent loops make it difficult to reason about stage responsibility, tool permissions, retries, and evaluation attribution.

## Decision

Use an explicit state graph with these ordered nodes:

1. build contract
2. retrieve evidence
3. analyze pricing
4. guarded research
5. draft brief
6. verify brief
7. human review outside the graph execution boundary

## Consequences

Positive:

- visible node boundaries and stable event taxonomy
- deterministic tools can be inserted where appropriate
- task state is easy to persist and replay
- metrics can be attributed to a stage
- a human approval gate is explicit

Negative:

- less flexible than an unrestricted agent loop
- new task families require explicit graph design
- complex conditional routing must be modeled rather than improvised

This trade-off is intentional: controlled enterprise delegation values auditability and reliability over theatrical autonomy.
