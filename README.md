# LLM Serving Lab

A hands-on playground for demonstrating how Large Language Models (LLMs) are served and consumed through different inference backends.

The project separates **model serving** from **model consumption**: the same client code talks to different serving backends (vLLM, Ollama, a baseline FastAPI server) through an OpenAI-compatible API.

## Status

Sprints 1-6 are complete: repository scaffolding, the serving backends
(baseline FastAPI, vLLM, Ollama), the client layer (raw-http + OpenAI SDK),
and the benchmarks. See [05 - Running Cookbook](docs/05-running-cookbook.md)
for how to start a server and consume it with the clients.

## Prerequisites

- Python 3.11+ and [uv](https://docs.astral.sh/uv/) for running tests.
- One or more of the serving backends (vLLM, Ollama) — see each sprint plan for install details.
- A NVIDIA GPU for vLLM; Ollama and the baseline server run on CPU.

## Configuration

Configuration is backend-neutral through three shared variables:

| Variable | Meaning |
|---|---|
| `OPENAI_BASE_URL` | OpenAI-compatible API base URL (includes `/v1`) |
| `OPENAI_API_KEY` | API key (self-hosted backends usually accept `demo`) |
| `MODEL_NAME` | Model served by the selected backend |

- `.env.example` documents the contract; copy it to `.env` to override defaults.
- `configs/models.env` holds the default model; `configs/endpoints.env` holds each backend's base URL.
- `profiles/*.env` hold backend-specific values. The Makefile sources the shared config plus a profile before running any command.

## Running the backends

The Makefile sources the relevant profile for you:

```bash
make serve-baseline   # baseline FastAPI server
make serve-vllm       # vLLM server
make serve-ollama     # Ollama server
```

The actual server runners are implemented in Sprints 2-4; until then the targets print the effective `OPENAI_BASE_URL` / `MODEL_NAME`.

## Using the clients

Clients are backend-neutral: point any OpenAI-compatible client at `OPENAI_BASE_URL` with `API_KEY` and `MODEL_NAME`, and the same code works against every backend. Concrete client examples (`clients/`) land in Sprint 5.

## Development

Run the test suite:

```bash
uv run pytest -v
```

## Documentation

- [01 - Project Concept Overview](docs/01-project-concept-overview.md)
- [02 - Project Architecture](docs/02-project-architecture.md)
- [03 - Project Scope](docs/03-project-scope.md)
- [04 - Technical Stack](docs/04-project-technical-stack.md)
- [05 - Running Cookbook](docs/05-running-cookbook.md)
- [06 - Benchmark Running Cookbook](docs/06-benchmark-running-cookbook.md)
- [Global Project Plan](docs/PLAN.md)
