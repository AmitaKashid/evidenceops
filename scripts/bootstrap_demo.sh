#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f .env ]]; then
  cp .env.example .env
fi

python -m venv backend/.venv
# shellcheck disable=SC1091
source backend/.venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e 'backend[dev]'
python -m app.services.seed_demo

echo "Backend is ready. Run: cd backend && uvicorn app.main:app --reload --port 8000"
echo "Frontend is ready after: cd frontend && npm install && npm run dev"
