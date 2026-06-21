# Validation record

Validated locally on 21 June 2026 using the repository's synthetic demo corpus.

## Automated checks

| Check | Result |
|---|---|
| Backend unit and integration tests | 7 passed |
| Backend lint | Ruff passed |
| Backend type checking | mypy passed for 51 application files |
| Frontend type checking | TypeScript passed |
| Frontend lint | ESLint passed |
| Next.js production generation | Build artifact created successfully |

## Live API smoke test

A live `POST /api/v1/tasks/runs` call with the bundled vendor-selection prompt returned:

| Signal | Observed result |
|---|---:|
| Run status | `waiting_for_review` |
| Provisional recommendation | `Northstar` |
| Quality score | `0.84` |
| Citation coverage | `1.00` |
| Citation precision | `1.00` |
| Numeric accuracy | `1.00` |
| Persisted execution events | `9` |
| Human review gate | enabled |

The score is capped below 1.0 because the scenario intentionally retains governance questions for manual review. This is desired behavior for a consequential workflow.

## Evaluation smoke test

A two-case benchmark across three configured profiles returned six results and completed successfully. The summary correctly reports no winner because every local profile uses the same deterministic provider. The local benchmark therefore validates evaluation infrastructure and report plumbing, not real foundation-model performance.

To make performance claims, configure approved real models through the OpenAI-compatible adapter, fix all other conditions, and rerun the versioned TaskBench.

## Not executed in this environment

Docker was not available in the validation runtime, so the Docker Compose topology was inspected but not launched here.
