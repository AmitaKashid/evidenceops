# Threat model and safety controls

## Scope

This document is a compact threat-model starting point for the EvidenceOps reference implementation. It is not a certification or a substitute for a formal security assessment.

## Assets

- confidential user requests
- uploaded or connected documents
- source metadata and retrieval results
- pricing and calculation outputs
- model-provider credentials
- workflow traces and reviewer decisions
- tenant isolation boundary

## Threats and controls

| Threat | Example | Control in reference project | Production control needed |
|---|---|---|---|
| Prompt injection in documents | A vendor PDF instructs the agent to ignore policy | Typed task contract, source constraints, deterministic verifier | Content sanitization, classifier, tool-level policies, red-team tests |
| Unsupported claim | Model recommends a vendor without evidence | Material claim citations and verifier | Entailment model, reviewer threshold, critical claim policies |
| Numerical hallucination | Report invents a total cost | pandas TCO tool and reconciliation rule | Signed calculation artifacts, versioned finance formulas |
| Cross-tenant data access | Tenant A retrieves Tenant B document | Tenant ID filtering in repository | Verified identity, row-level security, audit controls |
| Sensitive telemetry | Raw prompts stored in traces | Redaction helper and payload truncation | DLP, configurable retention, encryption, access control |
| Unauthorized action | Agent sends an email or changes procurement record | Read-only default and human review gate | Capability tokens, approval workflows, immutable audit log |
| Model supply-chain change | Provider model changes behavior | Profile abstraction and TaskBench runner | Model version pinning, canary tests, routing rollback |
| Retrieval poisoning | Misleading uploaded document outranks policy | Source metadata and internal-source prior | Approval workflow, source trust scoring, content provenance |

## Security invariants

1. A task cannot access documents outside its tenant scope.
2. A material claim must reference source IDs from the task’s retrieved evidence.
3. Numeric business claims must reconcile against deterministic calculations where available.
4. Irreversible actions are out of scope for the default workflow.
5. Remote model access is off by default.
6. Workflow changes should be evaluated before rollout.

## Logging guidance

Operational logs must remain useful without becoming a data leak. Store IDs, hashes, scores, stage timings, policy decisions, and bounded previews. Avoid unrestricted raw prompts, documents, model outputs, secrets, and credentials in telemetry.
