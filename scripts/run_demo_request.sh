#!/usr/bin/env bash
set -euo pipefail

curl -sS -X POST "${API_URL:-http://localhost:8000}/api/v1/tasks/runs" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: demo-tenant" \
  --data @- <<'JSON'
{
  "title": "Vendor selection decision brief",
  "model_profile": "enterprise-balanced",
  "request": "Review the approved vendor documents, compare all vendors against the internal security requirements, calculate a three-year total cost of ownership, identify policy gaps, and prepare a management decision brief with evidence citations. Escalate any unsupported conclusion."
}
JSON
