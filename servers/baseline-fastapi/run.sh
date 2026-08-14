#!/usr/bin/env bash
set -euo pipefail

# Start the educational baseline FastAPI server.
#
# Sources the shared model config plus the baseline profile so the server
# picks up OPENAI_BASE_URL / OPENAI_API_KEY / MODEL_NAME, then launches
# uvicorn on the port from OPENAI_BASE_URL (default 8080).

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

set -a
source "$ROOT/configs/models.env"
source "$ROOT/profiles/baseline.env"
set +a

PORT="${PORT:-8080}"
HOST="${HOST:-127.0.0.1}"

cd "$ROOT/servers/baseline-fastapi"

echo "==> Baseline FastAPI server: $OPENAI_BASE_URL (model=$MODEL_NAME)"
exec uvicorn app:app --host "$HOST" --port "$PORT"
