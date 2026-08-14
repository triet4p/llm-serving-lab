# Sprint 3 Plan

## Sprint Goal
Provide the vLLM serving backend as the main optimized OpenAI-compatible endpoint.

## Atomic Tasks
Status legend: [ ] pending / [~] in progress / [x] done

- [x] Task 1: Create `servers/vllm/config.env.example` documenting vLLM options (model, host, port, tensor-parallel size).
- [x] Task 2: Create `servers/vllm/run.sh` that sources the vLLM profile/config and runs `vllm serve <model> --host 0.0.0.0 --port 8000`.
- [x] Task 3: Create `servers/vllm/README.md` explaining GPU/driver/CUDA prerequisites and how to start the server.

## Notes / Blockers
- vLLM is the central backend (docs 01 §6, docs 04 §3).
- Requires a Linux + NVIDIA GPU server; the developer machine only sends requests (docs 04 §12).
