# ADR 0002: Verify critical output with deterministic rules first

## Status
Accepted

## Context

LLM-as-a-judge can be useful for nuanced quality assessment but cannot be the only control for material claims, source references, or arithmetic.

## Decision

Use deterministic rules for:

- citation membership in the retrieved evidence set
- material claim coverage
- lexical support proxy for source linkage
- numeric reconciliation against the pricing tool
- output completeness

LLM-based or human review may be added as layered assessment rather than replacing these checks.

## Consequences

The verifier is explainable and repeatable but conservative. It can create false warnings for valid paraphrases. That is preferable in this project because the review workflow can resolve warnings and the evaluation suite can measure the trade-off.
