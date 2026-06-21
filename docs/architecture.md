# EvidenceOps architecture

## Thesis

EvidenceOps is designed around **controlled delegation**, not open-ended autonomy. A user provides a complex business objective. The system converts it into typed workflow state, retrieves approved evidence, invokes deterministic tools where calculation is required, drafts a structured decision brief, validates the resulting claims, and waits for a reviewer decision.

```text
User objective
   │
   ▼
Task Contract ──► Approved-source retrieval ──► Deterministic analysis
   │                                                   │
   └────────► Provider abstraction ──► Decision Brief ┘
                                             │
                                             ▼
                               Citation + numeric verification
                                             │
                          ┌──────────────────┴──────────────────┐
                          ▼                                     ▼
                Human review required                  Approved automatically
                          │
                          ▼
                   Persistent trace
                          │
                          ▼
               TaskBench / release gates
```

## Runtime components

| Component | Responsibility | Key control |
|---|---|---|
| `TaskOrchestrator` | Creates persisted runs, emits events, maps workflow state to API output | Tenant-scoped database reads and writes |
| `WorkflowExecutor` | Runs the state graph and records stage timing | Explicit stage boundaries instead of hidden agent loops |
| `WorkflowNodes` | Builds contracts, retrieves sources, calculates costs, drafts, verifies | Narrow single-purpose nodes |
| `HybridRetriever` | Chunks documents and ranks approved evidence | Document allow-list and source type metadata |
| `PricingAnalysisTool` | Calculates three-year cost of ownership | Deterministic pandas calculation |
| `DecisionModelProvider` | Generates a structured decision brief | Local deterministic default and optional remote adapter |
| `ClaimVerifier` | Checks source legitimacy, support proxy, and numeric reconciliation | Independent non-LLM checks |
| `EvaluationRunner` | Replays TaskBench across configured model profiles | Versioned evaluation cases and comparable inputs |

## State model

The graph uses a shared state object. Nodes add structured fields rather than overwriting raw data with prose. Key state fields are:

- `contract` with objective, required capabilities, quality bar, and escalation conditions
- `retrieved_evidence` with document IDs, chunk IDs, sections, excerpts, and scores
- `pricing_results` with reproducible calculation inputs and outputs
- `decision_brief` with claims, citations, assumptions, and next actions
- `verification` with quality score, citation metrics, numeric accuracy, and issues
- `stage_metrics` with observed execution timing

This aligns with a durable-workflow design: when persistence is upgraded beyond the local demo, a run can be resumed from a stored state boundary rather than reconstructed from a chat transcript.

## Provider architecture

The default `DeterministicDecisionProvider` makes the repository runnable without model credentials. It is intentionally not presented as model intelligence. It is a transparent rules-based reference provider that proves the contracts, verification, and evaluation system.

`OpenAICompatibleDecisionProvider` provides a guarded integration seam. Remote inference remains disabled by default. Enabling it requires:

1. An approved endpoint and data-processing agreement.
2. A configured model and API key through environment variables.
3. Customer-specific policy for what content may leave the tenant boundary.
4. Evaluation evidence before routing consequential tasks to that provider.

## Production evolution

The architecture has clear upgrade seams:

| Demo implementation | Production replacement |
|---|---|
| SQLite | PostgreSQL with row-level tenant enforcement and backup policy |
| In-process graph | Durable LangGraph checkpointer plus background worker queue |
| Lexical/semantic proxy retrieval | pgvector or managed vector store with embedding versioning |
| Curated offline public research | Governed search connector with source allow-lists, caching, and content scanning |
| Header-based tenant identifier | OIDC/SAML authentication and verified claims |
| Local event records | OpenTelemetry collector, metrics backend, trace retention policy |

## Data boundaries

The demo data is synthetic. The code stores only data needed for the local demonstration. In a real deployment, the following must be decided per tenant:

- data classification and source allow-list
- retention and deletion window
- encrypted storage and key ownership
- trace payload redaction policy
- model and region allow-list
- review thresholds and approver roles
- cross-border transfer policy
