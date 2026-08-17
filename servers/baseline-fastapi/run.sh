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

# An exported MODEL_NAME overrides the profile default. Capture it before the
# profile sources its own MODEL_NAME, then restore it afterwards.
PRE_MODEL="${MODEL_NAME:-}"
set -a
source "$ROOT/configs/models.env"
source "$ROOT/profiles/baseline.env"
set +a
export MODEL_NAME="${PRE_MODEL:-$MODEL_NAME}"

PORT="${PORT:-8080}"
HOST="${HOST:-0.0.0.0}"

# Pre-download the model so serving never downloads on first request.
echo "==> Pre-downloading model $MODEL_NAME"
uv run python -c "from huggingface_hub import snapshot_download; snapshot_download('$MODEL_NAME')"

cd "$ROOT/servers/baseline-fastapi"

echo "==> Baseline FastAPI server: $OPENAI_BASE_URL (model=$MODEL_NAME)"
exec uvicorn app:app --host "$HOST" --port "$PORT"
