#!/usr/bin/env bash
set -euo pipefail

# Backend-neutral chat completion via curl.
#
# Uses the shared configuration contract OPENAI_BASE_URL / OPENAI_API_KEY /
# MODEL_NAME (see .env.example and configs/models.env). Point it at any
# OpenAI-compatible backend by exporting the right values first, e.g.:
#
#   export OPENAI_BASE_URL=http://localhost:8000/v1   # vLLM
#   export OPENAI_BASE_URL=http://localhost:11434/v1  # Ollama
#   export OPENAI_BASE_URL=http://localhost:8080/v1   # baseline FastAPI
#   export OPENAI_API_KEY=demo
#   export MODEL_NAME=Qwen/Qwen3-8B
#   bash clients/raw-http/curl-chat.sh
#
# Or source a backend profile so the three variables are set for you:
#   set -a; source profiles/vllm.env; set +a
#   bash clients/raw-http/curl-chat.sh

: "${OPENAI_BASE_URL:?Set OPENAI_BASE_URL (e.g. http://localhost:8000/v1), see .env.example}"
: "${OPENAI_API_KEY:?Set OPENAI_API_KEY (e.g. demo), see .env.example}"
: "${MODEL_NAME:?Set MODEL_NAME (e.g. Qwen/Qwen3-8B), see .env.example}"

curl -sS "$OPENAI_BASE_URL/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d "$(cat <<EOF
{
  "model": "$MODEL_NAME",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain in one sentence what an LLM serving engine does."}
  ],
  "max_tokens": 128,
  "temperature": 0.7
}
EOF
)"
