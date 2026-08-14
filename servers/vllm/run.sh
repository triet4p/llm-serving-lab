#!/usr/bin/env bash
set -euo pipefail

# Start the vLLM serving backend (OpenAI-compatible endpoint).
#
# Sources the shared model config (configs/models.env) plus the vLLM profile
# (profiles/vllm.env), then optionally the per-server config
# (servers/vllm/config.env, copied from config.env.example) so that
# MODEL_NAME / HOST / PORT / TENSOR_PARALLEL_SIZE are configurable. Finally
# launches `vllm serve` bound to 0.0.0.0 on the configured port.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

set -a
source "$ROOT/configs/models.env"
source "$ROOT/profiles/vllm.env"
if [[ -f "$ROOT/servers/vllm/config.env" ]]; then
    source "$ROOT/servers/vllm/config.env"
fi
set +a

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
TENSOR_PARALLEL_SIZE="${TENSOR_PARALLEL_SIZE:-1}"

echo "==> vLLM server: http://$HOST:$PORT/v1 (model=$MODEL_NAME, tensor_parallel_size=$TENSOR_PARALLEL_SIZE)"

exec vllm serve "$MODEL_NAME" \
    --host "$HOST" \
    --port "$PORT" \
    --tensor-parallel-size "$TENSOR_PARALLEL_SIZE"
