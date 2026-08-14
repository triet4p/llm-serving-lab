# Sprint 2 Plan

## Sprint Goal
Implement the educational baseline FastAPI serving layer that wraps `model.generate()` behind an OpenAI-compatible chat completions endpoint.

## Atomic Tasks
Status legend: [ ] pending / [~] in progress / [x] done

- [x] Task 1: Create `servers/baseline-fastapi/requirements.txt` pinning `fastapi`, `uvicorn`, `transformers`, and `torch`.
- [x] Task 2: Create `servers/baseline-fastapi/app.py` with FastAPI app setup and model/tokenizer loading via `AutoTokenizer`/`AutoModelForCausalLM`.
- [x] Task 3: Add the `POST /v1/chat/completions` endpoint (request parsing, tokenizer call, `model.generate()`, response serialization) to `app.py`.
- [x] Task 4: Add model-generation configuration (max tokens, temperature) read from request body in `app.py`.
- [x] Task 5: Create `servers/baseline-fastapi/run.sh` that sources the profile and launches uvicorn.

## Notes / Blockers
- This backend is educational only; it makes loading/generation/concurrency visible (docs 02 §4.1).
- No streaming, batching, or concurrency optimization required — keep it simple (docs 01 §7).
