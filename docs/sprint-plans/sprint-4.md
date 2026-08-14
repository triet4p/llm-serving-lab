# Sprint 4 Plan

## Sprint Goal
Provide the Ollama serving backend as an alternative OpenAI-compatible endpoint to demonstrate backend interchangeability.

## Atomic Tasks
Status legend: [ ] pending / [~] in progress / [x] done

- [ ] Task 1: Create `servers/ollama/Modelfile` defining the model and its serving parameters.
- [ ] Task 2: Create `servers/ollama/run.sh` that creates the model from the Modelfile and starts `ollama serve`.
- [ ] Task 3: Create `servers/ollama/README.md` explaining prerequisites and how to start the server.

## Notes / Blockers
- Ollama's role is backend interchangeability, not throughput (docs 02 §4.3).
- Keep generic clients free of Ollama-specific logic (docs 04 §5).
