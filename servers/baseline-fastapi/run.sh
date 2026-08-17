#!/usr/bin/env bash
set -euo pipefail

# Start the educational baseline FastAPI server.
#
# The baseline loads the model with Hugging Face Transformers + torch, so it
# must run on the GPU server (the same box as vLLM) rather than the developer
# machine. It sources the shared model config plus the baseline profile so the
# server picks up OPENAI_BASE_URL / OPENAI_API_KEY / MODEL_NAME, then launches
# uvicorn bound to 0.0.0.0 on the port from OPENAI_BASE_URL (default 8080) so
# the developer machine can reach it over the network.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

set -a
source "$ROOT/configs/models.env"
source "$ROOT/profiles/baseline.env"
set +a

PORT="${PORT:-8080}"
HOST="${HOST:-0.0.0.0}"

cd "$ROOT/servers/baseline-fastapi"

echo "==> Baseline FastAPI server: $OPENAI_BASE_URL (model=$MODEL_NAME)"
exec uvicorn app:app --host "$HOST" --port "$PORT"
