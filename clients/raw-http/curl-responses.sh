#!/usr/bin/env bash
set -euo pipefail

# Backend-neutral Responses API call via curl.
#
# Uses the shared configuration contract OPENAI_BASE_URL / OPENAI_API_KEY /
# MODEL_NAME (see .env.example and configs/models.env). The Responses API is a
# per-backend capability (docs 04 §7): not every OpenAI-compatible backend
# exposes POST /v1/responses yet (e.g. the baseline FastAPI server does not).
# Point it at a backend that supports it, e.g.:
#
#   export OPENAI_BASE_URL=http://localhost:8000/v1   # vLLM (recent versions)
#   export OPENAI_API_KEY=demo
#   export MODEL_NAME=Qwen/Qwen3-8B
#   bash clients/raw-http/curl-responses.sh
#
# Or source a backend profile so the three variables are set for you:
#   set -a; source profiles/vllm.env; set +a
#   bash clients/raw-http/curl-responses.sh

: "${OPENAI_BASE_URL:?Set OPENAI_BASE_URL (e.g. http://localhost:8000/v1), see .env.example}"
: "${OPENAI_API_KEY:?Set OPENAI_API_KEY (e.g. demo), see .env.example}"
: "${MODEL_NAME:?Set MODEL_NAME (e.g. Qwen/Qwen3-8B), see .env.example}"

curl -sS "$OPENAI_BASE_URL/responses" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d "$(cat <<EOF
{
  "model": "$MODEL_NAME",
  "input": "Explain in one sentence what an LLM serving engine does.",
  "max_output_tokens": 128
}
EOF
)"
