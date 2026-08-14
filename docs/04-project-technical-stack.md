# Project Technical Stack

## 1. Stack Overview

The project uses a deliberately small technical stack centered around Python, HTTP APIs, and GPU-based LLM inference.

```text
Client Layer
    |
    |  curl / Python / OpenAI SDK / Agent
    |
    v
HTTP API
    |
    v
Serving Layer
    |
    +-- vLLM
    +-- Ollama
    +-- FastAPI baseline
    |
    v
Model Runtime
    |
    v
GPU
```

## 2. Programming Language

### Python

Python is the primary implementation language.

Used for:

- the baseline inference server;
- API clients;
- benchmark scripts;
- utility scripts where appropriate.

Recommended baseline:

```text
Python 3.11+
```

Exact version should be aligned with the selected vLLM release and deployment environment.

## 3. Primary Serving Backend

### vLLM

Role:

- main LLM inference engine;
- optimized model serving;
- OpenAI-compatible API endpoint;
- concurrent request handling;
- batching and scheduling.

Typical command:

```bash
vllm serve <model-name>   --host 0.0.0.0   --port 8000
```

vLLM is the central technology demonstrated by the project.

## 4. Baseline Serving Stack

### FastAPI

Used to create a simple custom HTTP serving layer.

Responsibilities may include:

- request validation;
- generation endpoint;
- model invocation;
- response serialization.

### Uvicorn

Used as the ASGI server for the FastAPI baseline.

### Hugging Face Transformers

Used for manually loading and invoking the model in the baseline implementation.

Example conceptual flow:

```python
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

outputs = model.generate(...)
```

This stack provides the educational baseline against which vLLM can be compared.

## 5. Alternative Serving Backend

### Ollama

Ollama is included as an alternative inference backend.

Its main purposes are:

- demonstrate backend interchangeability;
- provide a simple serving comparison;
- show how API compatibility reduces client coupling.

The project should avoid making Ollama-specific logic a dependency of generic clients.

## 6. Client Stack

### curl

Used for low-level HTTP demonstrations.

Advantages:

- no application abstraction;
- API request and response are visible;
- useful for smoke testing.

### OpenAI Python SDK

Used as the primary application-level client for OpenAI-compatible endpoints.

Typical configuration:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://gpu-server:8000/v1",
    api_key="demo",
)
```

The same client code should be reusable where backend compatibility allows.

### HTTP Client

Python libraries such as `httpx` may be used when raw HTTP access is useful.

## 7. API Protocols

The project may cover:

### OpenAI Chat Completions

```text
POST /v1/chat/completions
```

Primary use:

- conversational LLM calls;
- common compatibility layer.

### OpenAI Completions

```text
POST /v1/completions
```

Primary use:

- explaining the older prompt-based interface.

### OpenAI Responses API

Used to demonstrate the newer unified response model where supported.

### Anthropic Messages API

May be demonstrated when evaluating interoperability with Anthropic-style clients or tools.

Protocol support should always be treated as a capability of the selected serving backend rather than assumed universally.

## 8. Configuration

Environment variables are preferred over hard-coded endpoints.

Example:

```bash
OPENAI_BASE_URL=http://gpu-server:8000/v1
OPENAI_API_KEY=demo
MODEL_NAME=Qwen/Qwen3-8B
```

Suggested profiles:

```text
profiles/
├── baseline.env
├── vllm.env
└── ollama.env
```

## 9. Benchmark Stack

The first version should keep benchmarking lightweight.

Possible implementation:

- Python;
- `asyncio`;
- `httpx`;
- monotonic timers;
- basic JSON or CSV result output.

Metrics may include:

```text
Latency
Time to First Token
Total Generation Time
Requests / Second
Tokens / Second
Concurrency
```

A dedicated benchmarking framework can be introduced later if required.

## 10. Shell and Automation

### Bash

Used for:

- starting servers;
- exporting profiles;
- smoke tests;
- curl examples;
- demo orchestration.

### Makefile

Optional but recommended for common commands.

Example interface:

```bash
make serve-vllm
make serve-baseline
make smoke
make benchmark
```

The Makefile should provide convenience rather than hide important concepts.

## 11. Model Selection

The project should use an open-weight instruction or chat model that:

- runs on the available GPU;
- starts quickly enough for demonstrations;
- has a compatible tokenizer/chat template;
- works across as many selected serving backends as practical.

Model selection should be configurable rather than hard-coded into client logic.

## 12. Infrastructure

### GPU Server

Primary inference environment.

Typical requirements:

- Linux;
- NVIDIA GPU;
- compatible NVIDIA driver;
- CUDA environment required by the selected serving engine;
- network access from the client machine.

### Developer Machine

Used for:

- sending requests;
- running client code;
- benchmarks;
- agent integration;
- presentation/demo control.

The developer machine does not necessarily require a GPU.

## 13. Dependency Management

For a small demo repository, dependency management should remain simple.

Possible choices:

- `requirements.txt`;
- `pyproject.toml`;
- `uv`.

A single project-level dependency strategy is preferable to many unrelated environments unless the backend requires isolation.

## 14. Optional Future Technologies

Potential future additions include:

- Docker;
- Docker Compose;
- SGLang;
- Hugging Face TGI;
- llama.cpp;
- Prometheus;
- Grafana;
- Locust or k6;
- Kubernetes;
- NGINX or an API gateway;
- OpenTelemetry;
- multi-GPU inference.

These should be introduced only when they support a concrete learning or demonstration objective.

## 15. Technical Stack Summary

| Layer | Technology |
|---|---|
| Language | Python |
| Main LLM Server | vLLM |
| Baseline Server | FastAPI + Uvicorn + Transformers |
| Alternative Backend | Ollama |
| Client SDK | OpenAI Python SDK |
| Raw Client | curl / HTTP |
| Async HTTP | httpx |
| Benchmarking | Python + asyncio |
| Configuration | Environment variables |
| Automation | Bash / Makefile |
| Hardware | NVIDIA GPU server |
| Communication | HTTP / OpenAI-compatible APIs |
