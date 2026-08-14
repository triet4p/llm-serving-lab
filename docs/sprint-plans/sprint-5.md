# Sprint 5 Plan

## Sprint Goal
Implement backend-neutral clients: raw HTTP (`curl`) examples and OpenAI SDK scripts that work against any compatible backend via `BASE_URL` / `API_KEY` / `MODEL_NAME`.

## Atomic Tasks
Status legend: [ ] pending / [~] in progress / [x] done

- [ ] Task 1: Create `clients/raw-http/curl-chat.sh` with a `curl` request to `POST /v1/chat/completions`.
- [ ] Task 2: Create `clients/raw-http/curl-responses.sh` with a `curl` request to the Responses-style endpoint.
- [ ] Task 3: Create `clients/openai-sdk/chat_completions.py` using the OpenAI SDK with env-configured base URL.
- [ ] Task 4: Create `clients/openai-sdk/completions.py` for the prompt-based completions interface.
- [ ] Task 5: Create `clients/openai-sdk/responses.py` for the Responses API where supported.

## Notes / Blockers
- Application logic must stay unchanged across backends (docs 02 §5, docs 03 §2.5).
- Treat protocol support as a per-backend capability, not universal (docs 04 §7).
