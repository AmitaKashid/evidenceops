#!/usr/bin/env bash
set -euo pipefail

curl -sS -X POST "${API_URL:-http://localhost:8000}/api/v1/evaluations/runs" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: demo-tenant" \
  --data '{"model_profiles":["enterprise-fast","enterprise-balanced","enterprise-precise"]}'
