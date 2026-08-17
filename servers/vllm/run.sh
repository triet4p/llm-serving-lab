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

# An exported MODEL_NAME overrides the profile/config default. Capture it
# before the sources set their own MODEL_NAME, then restore it afterwards.
PRE_MODEL="${MODEL_NAME:-}"
set -a
source "$ROOT/configs/models.env"
source "$ROOT/profiles/vllm.env"
if [[ -f "$ROOT/servers/vllm/config.env" ]]; then
    source "$ROOT/servers/vllm/config.env"
fi
set +a
export MODEL_NAME="${PRE_MODEL:-$MODEL_NAME}"

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
TENSOR_PARALLEL_SIZE="${TENSOR_PARALLEL_SIZE:-1}"

# CUDA 13.0's nvcc refuses GCC versions later than 12 during runtime JIT
# (flashinfer cached-op builds), which aborts engine init with an
# "unsupported GNU version" error. Relax the version check and skip
# flashinfer's runtime JIT build. (See lessons-learned log.)
export NVCC_PREPEND_FLAGS="${NVCC_PREPEND_FLAGS:--allow-unsupported-compiler}"
export VLLM_USE_FLASHINFER="${VLLM_USE_FLASHINFER:-0}"

# Pre-download the model so vLLM serves from the local cache.
echo "==> Pre-downloading model $MODEL_NAME"
uv run python -c "from huggingface_hub import snapshot_download; snapshot_download('$MODEL_NAME')"

echo "==> vLLM server: http://$HOST:$PORT/v1 (model=$MODEL_NAME, tensor_parallel_size=$TENSOR_PARALLEL_SIZE)"

exec vllm serve "$MODEL_NAME" \
    --host "$HOST" \
    --port "$PORT" \
    --tensor-parallel-size "$TENSOR_PARALLEL_SIZE"
