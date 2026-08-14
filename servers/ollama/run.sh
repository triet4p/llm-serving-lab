#!/usr/bin/env bash
set -euo pipefail

# Start the Ollama serving backend (OpenAI-compatible endpoint).
#
# Sources the shared model config (configs/models.env) plus the Ollama profile
# (profiles/ollama.env). The ollama CLI talks to the local daemon, so the
# server is started in the background first, then the model is created from
# the Modelfile (skipped when already present), and finally the server is kept
# in the foreground. OLLAMA_HOST overrides the default bind address.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

set -a
source "$ROOT/configs/models.env"
source "$ROOT/profiles/ollama.env"
set +a

OLLAMA_HOST="${OLLAMA_HOST:-0.0.0.0:11434}"
OLLAMA_PORT="${OLLAMA_HOST##*:}"
MODEL_NAME="${MODEL_NAME:-qwen3:8b}"
MODELFILE="$ROOT/servers/ollama/Modelfile"

export OLLAMA_HOST

echo "==> Ollama server: $OPENAI_BASE_URL (model=$MODEL_NAME)"

# The ollama CLI requires the daemon, so start it in the background first.
ollama serve &
OLLAMA_PID=$!
trap 'kill "$OLLAMA_PID" 2>/dev/null || true' EXIT

# Wait until the daemon accepts requests (up to 30 seconds).
for _ in $(seq 1 30); do
    if curl -sf "http://localhost:$OLLAMA_PORT/api/version" >/dev/null 2>&1; then
        break
    fi
    sleep 1
done

if ollama list | grep -q "^${MODEL_NAME}[[:space:]]"; then
    echo "==> Model $MODEL_NAME already present; skipping creation."
else
    echo "==> Creating model $MODEL_NAME from the Modelfile."
    ollama create "$MODEL_NAME" -f "$MODELFILE"
fi

echo "==> Serving (Ctrl-C to stop)."
wait "$OLLAMA_PID"
