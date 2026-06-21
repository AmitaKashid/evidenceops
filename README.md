# EvidenceOps

**EvidenceOps** is a governed decision-brief agent and evaluation control plane for enterprise power users. It turns a complex request plus approved documents and spreadsheets into an auditable recommendation with cited evidence, numeric checks, human approval gates, and replayable evaluation results.

> This repository is a portfolio-grade reference implementation. It is intentionally opinionated: bounded orchestration, evidence-first outputs, deterministic verification, and measurable quality matter more than unconstrained autonomy.

## Why it exists

Most AI workspaces make it easy to ask a model a question. Enterprise teams need more than an answer: they need a traceable workflow that can combine internal documents, pricing data, policy requirements, and selected external research without hiding assumptions or fabricating evidence.

EvidenceOps demonstrates that operating model through a vendor-selection decision brief:

1. Convert a natural-language request into a validated task contract.
2. Retrieve evidence from approved sources using hybrid ranking.
3. Analyze vendor-pricing data with deterministic calculations.
4. Draft a decision brief through a model-provider abstraction.
5. Verify citations, numbers, and escalation conditions.
6. Pause for human approval and persist a complete execution trace.
7. Replay versioned evaluation cases to compare policies or model profiles.

## Product surfaces

| Surface | What it demonstrates |
|---|---|
| **Task Studio** | A bounded agent workflow from request to review-ready brief |
| **Evidence Ledger** | Claim-to-source traceability and numeric validation |
| **Evaluation Control Plane** | TaskBench execution, model-profile comparison, regression detection |
| **Observability** | Run events, stage latency, tool usage, verifier outcomes, redaction-aware payloads |
| **Governance** | Tenant scoping, source allow-lists, human approval gate, safe defaults |

## Repository layout

```text
EvidenceOps/
├── backend/                  # FastAPI API, workflow engine, evaluation runner, SQLite persistence
├── frontend/                 # Next.js dashboard for tasks, runs, evidence, and evaluations
├── docs/                     # Architecture, evaluation protocol, threat model, ADRs, demo guide
├── scripts/                  # Local bootstrap and convenience scripts
├── .github/workflows/        # CI for linting, tests, and frontend checks
├── docker-compose.yml        # Local full-stack development topology
└── Makefile                  # Common commands
```

## Quick start

### Option A: Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

Open the dashboard at `http://localhost:3000` and the API documentation at `http://localhost:8000/docs`.

### Option B: local development

```bash
# Terminal 1
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e '.[dev]'
uvicorn app.main:app --reload --port 8000

# Terminal 2
cd frontend
npm install
npm run dev
```

The backend seeds an intentionally small demo corpus and an evaluation suite on first start.

## Demo task

Use the following request in the Task Studio:

> Review the approved vendor documents, compare all vendors against the internal security requirements, calculate a three-year total cost of ownership, identify policy gaps, and prepare a management decision brief with evidence citations. Escalate any unsupported conclusion.

The seeded corpus is synthetic and clearly labelled. It exists to make the project fully runnable without exposing confidential data.

## API overview

| Endpoint | Purpose |
|---|---|
| `POST /api/v1/tasks/runs` | Execute a governed decision-brief workflow |
| `GET /api/v1/tasks/runs/{run_id}` | Retrieve the output, state, evidence, and verification result |
| `POST /api/v1/tasks/runs/{run_id}/review` | Record human approval, rejection, or requested changes |
| `GET /api/v1/evaluations/cases` | Inspect the versioned TaskBench cases |
| `POST /api/v1/evaluations/runs` | Run a benchmark against one or more model profiles |
| `GET /api/v1/dashboard/summary` | Retrieve dashboard metrics and recent activity |

## Design decisions

- **Bounded state graph over open-ended loops.** Each workflow node has a narrow responsibility and produces structured state.
- **Evidence first.** Every material recommendation must carry one or more source references.
- **Deterministic validators.** Citation and numeric checks do not rely solely on an LLM judge.
- **Human approval for consequential output.** The run pauses at a review gate before approval is recorded.
- **Evaluation as a product capability.** Real workflow changes should create regression tests, not only anecdotal demos.
- **No hidden production claims.** The default provider is deterministic and local. Configure an OpenAI-compatible endpoint only when you have approved credentials and a valid data-processing basis.

## Technology stack

| Layer | Technology | Why |
|---|---|---|
| API | FastAPI + Pydantic | Typed contracts, OpenAPI documentation, clean dependency boundaries |
| Workflow | LangGraph | Explicit state, inspectable node boundaries, durable-workflow extension point |
| Persistence | SQLAlchemy + SQLite | Runnable local storage with a straightforward upgrade path to PostgreSQL |
| Retrieval | Hybrid lexical + semantic-proxy ranking | Reproducible local retrieval without embedding vendor lock-in |
| Data analysis | pandas | Deterministic pricing and TCO calculations |
| Observability | OpenTelemetry interfaces + persisted run events | Traceable model and tool activity without storing unrestricted raw data |
| Frontend | Next.js + TypeScript | Typed dashboard routes and a clear app-router structure |
| Quality | pytest, Ruff, mypy, GitHub Actions | Regression-first development and CI gates |

## Important limitations

This is a reference system, not a security-certified production deployment. Before production use, add authentication and authorization integration, encrypted secret storage, customer-specific data retention controls, real document malware scanning, a managed vector database, rate limiting, background workers, and a reviewed threat model.

## License

MIT. See [LICENSE](LICENSE).
