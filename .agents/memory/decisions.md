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
