# Model routing strategy

## Principle

A router should select a **policy for a constrained task**, not assert that one model is globally best. A policy may differ by quality target, data sensitivity, tool use, task ambiguity, latency budget, and cost budget.

## Included profiles

| Profile | Intended use | Quality bias | Cost index | Latency target |
|---|---:|---:|---:|---:|
| `enterprise-fast` | extraction, routing, low-complexity drafting | 0.67 | 0.4× | 1.8 s |
| `enterprise-balanced` | normal decision briefs and cross-document synthesis | 0.82 | 1.0× | 4.2 s |
| `enterprise-precise` | high-ambiguity, high-value, or higher-risk analysis | 0.92 | 2.4× | 8.2 s |

In this local reference implementation, profiles run through the same deterministic provider to validate the evaluation plumbing. They must be connected to approved real models before performance claims are made.

## Routing features

A production router can use:

- request complexity and document count
- expected tool use and numeric calculation needs
- source conflict or ambiguity score
- output consequence and human-review policy
- tenant-approved model list and processing region
- measured task-family quality, cost, and latency history

## Router decision record

Every decision should produce a record with:

```json
{
  "task_type": "evidence_grounded_decision_brief",
  "selected_profile": "enterprise-balanced",
  "candidate_profiles": ["enterprise-fast", "enterprise-balanced"],
  "selection_reason": ["cross_document_synthesis", "pricing_calculation", "human_review_required"],
  "quality_budget": 0.8,
  "latency_budget_ms": 5000,
  "cost_budget_usd": 0.05,
  "router_version": "2026.06.1"
}
```

This makes routing explainable and replayable.
