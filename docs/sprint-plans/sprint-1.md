# Sprint 1 Plan

## Sprint Goal
Establish the repository scaffolding, configuration profiles, and convenience commands so later backends and clients have a consistent place to live.

## Atomic Tasks
Status legend: [ ] pending / [~] in progress / [x] done

- [x] Task 1: Create the top-level directory layout (`servers/`, `clients/`, `benchmarks/`, `configs/`, `profiles/`, `scripts/`, `slides/`) with `.gitkeep` files for empty dirs.
- [x] Task 2: Create `.env.example` documenting the shared variables `OPENAI_BASE_URL`, `OPENAI_API_KEY`, and `MODEL_NAME`.
- [x] Task 3: Create `configs/models.env` with the default model choice and `configs/endpoints.env` with the backend base URLs.
- [x] Task 4: Create `profiles/baseline.env` with baseline-specific `OPENAI_BASE_URL`/`MODEL_NAME` values.
- [x] Task 5: Create `profiles/vllm.env` with vLLM-specific `OPENAI_BASE_URL`/`MODEL_NAME` values.
- [x] Task 6: Create `profiles/ollama.env` with Ollama-specific `OPENAI_BASE_URL`/`MODEL_NAME` values.
- [x] Task 7: Create a Makefile with convenience targets (`serve-vllm`, `serve-baseline`, `serve-ollama`, `smoke`, `benchmark`, `health`) that source the relevant profile.
- [x] Task 8: Update `README.md` to describe the project, prerequisites, and how to run each backend/client (replace the "planning phase" status).

## Notes / Blockers
- Model name in `configs/models.env` should be configurable, not hard-coded (per docs 04 §11).
- Confirm exact `OPENAI_BASE_URL` per backend when each server is implemented in later sprints.
