# Decisions

## [2026-08-14] OpenAI SDK clients declare their dependency via uv inline script metadata

**Decision:** All `clients/openai-sdk/*.py` scripts use PEP 723 inline script metadata (`# /// script` block with `dependencies = ["openai>=1.0"]`) and are run with `uv run clients/openai-sdk/<name>.py`. `openai` is NOT added to the project's `pyproject.toml` dev dependency group.

**Alternatives considered:** Adding `openai` to `[dependency-groups].dev` in `pyproject.toml` so scripts use the shared venv.

**Reason:** The client scripts are standalone utility scripts (docs 04 §6) that must stay backend-neutral and clone-and-run friendly. Declaring the dependency inside each script keeps them self-contained, avoids coupling the project's dev environment to a large SDK that is only needed by demo clients, and follows the project-wide rule for standalone scripts (per the shared python rules).

**Consequences:** Running the SDK clients requires `uv` (already a project prerequisite) and will resolve the `openai` dependency on first run per script. Tests for these scripts must be content assertions (they cannot import `openai` inside the project venv), mirroring the sprint 3/4 README/script test pattern. Future SDK clients (e.g. benchmarks) should keep this inline-metadata approach.

## [2026-08-14] Clients consume the shared env contract, never backend-specific config

**Decision:** Every client (`clients/raw-http/*.sh` and `clients/openai-sdk/*.py`) reads exactly `OPENAI_BASE_URL`, `OPENAI_API_KEY`, `MODEL_NAME` from the environment and hard-fails with a helpful message when any is missing. No client reads backend profiles (`profiles/*.env`) or hard-codes an endpoint/model.

**Alternatives considered:** Having clients source a backend profile (e.g. `profiles/vllm.env`) by default; having clients pick a default base URL like `http://localhost:8000/v1`.

**Reason:** Backend switching must require "as little application change as possible" (docs 02 §6, docs 03 §2.5) — the application logic must stay identical across vLLM/Ollama/baseline and only the configuration changes. Sourcing a profile inside a client would couple it to one backend and defeat the interchangeability demo.

**Consequences:** Users must export the three variables (or source a profile themselves, e.g. `set -a; source profiles/vllm.env; set +a`) before running a client. The scripts remain dependency-free of the project layout and work from anywhere once the env contract is set.

## [2026-08-17] Benchmarks are self-contained httpx scripts, not shared-module or SDK-based

**Decision:** All `benchmarks/*.py` are standalone scripts that use `httpx` (declared via PEP 723 inline metadata, run with `uv run --script`), consume the same `OPENAI_BASE_URL` / `OPENAI_API_KEY` / `MODEL_NAME` env contract as clients, and duplicate the small streaming/SSE and `save_results()` helpers inline rather than importing a shared `benchmarks/_bench.py` module.

**Alternatives considered:** Using the `openai` SDK instead of raw `httpx`; extracting shared helpers into a `benchmarks/_bench.py` module; introducing a dedicated benchmarking framework (Locust/k6).

**Reason:** docs 04 §9 requires a lightweight stack (Python + asyncio + httpx + monotonic timers), and raw `httpx` gives direct control over streaming/TTFT measurement that the SDK abstracts away. A shared module was avoided because `uv run --script` resolves deps per script and sibling imports are not guaranteed, so scripts stay clone-and-run friendly as standalone utilities (mirroring the Sprint 5 client decision). Duplicated helpers are ~25 lines of stdlib code — acceptable to keep each script independent. A dedicated framework is explicitly deferred (docs 04 §9).

**Consequences:** Refactoring the duplicated helper code into a shared module would be a deliberate change that must be validated under `uv run --script`. Tests for benchmarks must remain content assertions (they cannot import `httpx` inside the project venv). Results are gitignored (`benchmarks/results/`, only `.gitkeep` tracked).

## [2026-08-17] Baseline FastAPI runs on the GPU server, not the developer machine

**Decision:** The baseline FastAPI backend runs on the **same GPU server as vLLM** (the user's setup: `192.168.30.244`), never on the developer machine. `servers/baseline-fastapi/run.sh` binds `0.0.0.0` by default, and `profiles/baseline.env` / `configs/endpoints.env` set `OPENAI_BASE_URL=http://192.168.30.244:8080/v1` — the address clients on the developer machine use to reach it.

**Alternatives considered:** Running the baseline locally on the developer machine (`127.0.0.1:8080`, the original sprint-1 setting), which needs no GPU but requires installing Transformers + torch on the laptop.

**Reason:** The baseline loads the model with Hugging Face Transformers + torch (`servers/baseline-fastapi/app.py`), which is heavy and GPU-accelerated; the developer machine has no GPU and should stay a thin HTTP-only client (docs 04 §12). Co-locating the baseline with vLLM on the GPU server keeps a single model-loading environment and mirrors the two-machine demo topology in docs 02 §7.

**Consequences:** The baseline endpoint is reachable only when the GPU server is up. `OPENAI_BASE_URL` in `profiles/baseline.env` is deployment-specific (the GPU server IP); a different setup must edit it. Because the baseline is non-streaming, the sprint-6 streaming benchmarks cannot be used against it.
