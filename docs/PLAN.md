# Global Project Plan

## Overview

Build the **LLM Serving Lab**: a compact, clone-and-run playground that demonstrates how LLMs are served and consumed through different inference backends. It separates **model serving** (servers) from **model consumption** (clients) behind an OpenAI-compatible API contract, so the same client code works against vLLM, Ollama, and a hand-written FastAPI baseline.

The primary learning arc is: `model.generate()` → Python + FastAPI → dedicated serving (vLLM) → OpenAI-compatible API → applications / SDKs / agents. The project favors clarity over production complexity and stays demo-friendly.

## Milestones

- [x] **Milestone 1: Scaffolding** — repository layout, configuration profiles, environment template, and Makefile convenience commands.
- [ ] **Milestone 2: Serving backends** — baseline FastAPI server, vLLM runner, and Ollama runner, each exposing an OpenAI-compatible endpoint.
- [ ] **Milestone 3: Client layer** — raw HTTP (`curl`) examples and OpenAI SDK clients that are backend-neutral via `BASE_URL` / `API_KEY` / `MODEL_NAME`.
- [ ] **Milestone 4: Benchmarks** — single-request, latency, and concurrency benchmarks with JSON/CSV output.
- [ ] **Milestone 5: Automation & demo** — healthcheck, smoke-test, demo orchestration, agent integration, and slides.

## Active Sprints

- [Sprint 1](docs/sprint-plans/sprint-1.md) - *Status: Complete* — Scaffolding
- [Sprint 2](docs/sprint-plans/sprint-2.md) - *Status: Not Started* — Baseline FastAPI server
- [Sprint 3](docs/sprint-plans/sprint-3.md) - *Status: Not Started* — vLLM server
- [Sprint 4](docs/sprint-plans/sprint-4.md) - *Status: Not Started* — Ollama server
- [Sprint 5](docs/sprint-plans/sprint-5.md) - *Status: Not Started* — Client layer
- [Sprint 6](docs/sprint-plans/sprint-6.md) - *Status: Not Started* — Benchmarks
- [Sprint 7](docs/sprint-plans/sprint-7.md) - *Status: Not Started* — Automation, agents & slides

## Completed Sprints

- [Sprint 1](docs/sprint-plans/sprint-1.md) - *Complete* — Scaffolding

## Backlog / Future Work

- Additional backends: SGLang, Hugging Face TGI, llama.cpp.
- vLLM advanced features: tensor parallelism, speculative decoding, structured outputs, tool calling, prefix caching, quantized models.
- Observability: Prometheus metrics, Grafana dashboards, OpenTelemetry tracing.
- Deployment: Docker / Docker Compose, Kubernetes, NGINX/API gateway, multi-model request routing.
- Load testing with dedicated tools (Locust / k6).
