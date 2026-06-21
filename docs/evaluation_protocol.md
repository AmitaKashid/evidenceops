# Evaluation protocol

## Purpose

The evaluation system answers a practical question: **did a change make the workflow more useful and reliable for this task family without creating unacceptable cost, latency, or safety regressions?**

It does not attempt to crown one universal best model.

## TaskBench design

`backend/data/taskbench/cases.json` contains versioned cases across these categories:

| Category | Purpose |
|---|---|
| End-to-end vendor selection | Validate the complete contract → retrieve → analyze → draft → verify flow |
| Grounding and policy | Check whether material claims use expected approved sources |
| Numeric calculation | Validate total-cost calculations and contingency handling |
| Research governance | Confirm source restrictions and evidence framing |
| Adversarial unsupported instruction | Reward escalation instead of following an unsupported directive |

Every case defines expected source documents, expected claim fragments, the expected escalation decision, and optional vendor expectations.

## Fair comparison rule

A profile comparison holds constant:

- TaskBench version and task IDs
- approved document corpus
- retrieval configuration
- tool availability
- output schema
- verification rules
- evaluation scorer

Only the selected model profile or workflow policy should differ. If retrieval, prompts, tools, and model are changed at once, the result is a product experiment rather than a valid model comparison.

## Automated metrics

| Metric | Definition | Why it matters |
|---|---|---|
| Task completion | Required fragments, expected vendor where relevant, and expected source usage | Measures whether the output addressed the task |
| Citation coverage | Material claims with grounded support | Penalizes unsupported conclusions |
| Citation precision | Citations that belong to the run’s approved retrieval set | Prevents fabricated or stale source references |
| Numeric accuracy | Numerical material claims that reconcile with deterministic tool output | Avoids narrative arithmetic errors |
| Escalation correctness | Whether the system escalates when labelled conditions require it | Measures calibrated uncertainty and safety behavior |
| Composite score | Weighted combined score | Provides a concise release-gate signal, not a replacement for diagnostics |
| Latency | End-to-end observed run time | Makes operational trade-offs visible |
| Estimated cost | Configured profile estimate | Enables quality-cost decisions |

## Release gates

For any meaningful modification, create a baseline and candidate run over the impacted TaskBench subset.

Example gate:

```text
Candidate may proceed when:
- citation coverage does not decline by more than 2 percentage points
- numeric accuracy does not decline
- escalation correctness does not decline
- composite score increases or remains within 1 percentage point
- latency and cost remain within the service-level budget
- no new error-level verifier issues appear in adversarial cases
```

The exact threshold belongs to the operating team and task risk level.

## Human evaluation

Automated metrics are necessary but insufficient for a decision-support system. Add a blinded reviewer panel for periodic calibration:

1. Sample completed runs by task type and customer segment.
2. Hide profile names and candidate order.
3. Score usefulness, evidence sufficiency, decision clarity, and risk handling.
4. Record disagreements and adjudication rationale.
5. Convert recurring failures into TaskBench cases.

The human score should remain a separate dimension. Do not silently use a reviewer’s preference as a substitute for evidence-grounding metrics.

## Continuous improvement loop

```text
Trace or reviewer feedback
   → failure taxonomy
   → new labelled TaskBench case
   → isolated candidate change
   → offline replay and regression gate
   → shadow or limited rollout
   → production monitoring
```

This loop is the product moat: the system gets more reliable through evidence rather than through anecdotal prompt tweaking.
