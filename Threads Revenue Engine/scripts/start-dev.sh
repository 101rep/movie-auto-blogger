#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
test -f .env || { echo "Copy .env.example to .env and set ADMIN_PASSWORD"; exit 1; }
source .venv/bin/activate
python -m alembic upgrade head
python -m apps.backend.tre.seed
python -m uvicorn apps.backend.tre.main:app --host 127.0.0.1 --port 8000 &
backend_pid=$!
python -m apps.worker.main &
worker_pid=$!
trap 'kill "$backend_pid" "$worker_pid" 2>/dev/null || true' EXIT
cd apps/frontend
pnpm dev
