# Project Architecture

## 1. Architecture Overview

The project uses a modular architecture that separates serving backends from clients.

```text
+----------------------------------------------------------+
|                         Clients                          |
|                                                          |
|  curl     Python SDK     Benchmark     Agent / Tool      |
+-----------------------------+----------------------------+
                              |
                              |
                    HTTP / API Protocol
                              |
                  OpenAI-compatible API
                              |
        +---------------------+---------------------+
        |                     |                     |
        v                     v                     v
+---------------+     +---------------+     +---------------+
|     vLLM      |     |    Ollama     |     |   Baseline    |
|               |     |               |     | Python +      |
| LLM Serving   |     | Local /       |     | FastAPI       |
| Engine        |     | Simple Serve  |     |               |
+-------+-------+     +-------+-------+     +-------+-------+
        |                     |                     |
        +---------------------+---------------------+
                              |
                              v
                         Model Runtime
```

## 2. Architectural Principles

### 2.1 Client and Server Independence

Clients should not depend directly on a specific inference backend.

Instead of writing:

```text
client-vllm/
client-ollama/
client-fastapi/
```

the repository organizes clients by protocol or use case:

```text
clients/
├── raw-http/
├── openai-sdk/
└── agents/
```

Serving implementations are isolated under:

```text
servers/
├── baseline-fastapi/
├── vllm/
└── ollama/
```

This allows new serving backends to be introduced without rewriting the client layer.

## 3. Proposed Repository Structure

```text
llm-serving-demo/
├── README.md
├── .env.example
├── Makefile
│
├── docs/
│   ├── 01-project-concept-overview.md
│   ├── 02-project-architecture.md
│   ├── 03-project-scope.md
│   └── 04-project-technical-stack.md
│
├── servers/
│   ├── baseline-fastapi/
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   └── run.sh
│   │
│   ├── vllm/
│   │   ├── run.sh
│   │   ├── config.env.example
│   │   └── README.md
│   │
│   └── ollama/
│       ├── run.sh
│       ├── Modelfile
│       └── README.md
│
├── clients/
│   ├── raw-http/
│   │   ├── curl-chat.sh
│   │   └── curl-responses.sh
│   │
│   ├── openai-sdk/
│   │   ├── chat_completions.py
│   │   ├── responses.py
│   │   └── completions.py
│   │
│   └── agents/
│       ├── codex/
│       └── claude-code/
│
├── benchmarks/
│   ├── single_request.py
│   ├── concurrency.py
│   ├── latency.py
│   └── results/
│
├── configs/
│   ├── models.env
│   ├── endpoints.env
│   └── prompts/
│
├── profiles/
│   ├── baseline.env
│   ├── vllm.env
│   └── ollama.env
│
├── scripts/
│   ├── healthcheck.sh
│   ├── smoke-test.sh
│   └── demo.sh
│
└── slides/
```

## 4. Serving Layer

### 4.1 Baseline FastAPI

The baseline implementation demonstrates what happens when a developer builds a serving layer manually.

Typical flow:

```text
HTTP Request
     |
     v
FastAPI
     |
     v
Tokenizer
     |
     v
model.generate()
     |
     v
HTTP Response
```

This backend exists mainly for educational comparison.

It makes concerns such as request handling, model loading, generation configuration, concurrency, and batching visible.

### 4.2 vLLM

vLLM acts as the main optimized serving backend.

```text
Client
  |
  v
OpenAI-compatible API
  |
  v
vLLM API Server
  |
  v
Scheduler / Continuous Batching
  |
  v
KV Cache / Model Executor
  |
  v
GPU
```

The main architectural benefit is that the application-facing API and the inference engine are already integrated.

### 4.3 Ollama

Ollama provides an additional backend for comparison.

Its role is not necessarily to compete directly with vLLM on throughput, but to demonstrate that the client layer can remain largely unchanged across serving implementations.

## 5. Client Layer

### Raw HTTP

Useful for making the API contract visible.

Example:

```text
curl
  |
  v
POST /v1/chat/completions
```

### OpenAI SDK

Demonstrates API compatibility and backend interchangeability.

The main configuration becomes:

```text
BASE_URL
API_KEY
MODEL_NAME
```

The application logic remains largely unchanged.

### Agent Integration

The agent layer demonstrates that a self-hosted model can become infrastructure for higher-level developer tooling.

Conceptually:

```text
Coding Agent
     |
     v
OpenAI / Anthropic-style API
     |
     v
Self-hosted inference endpoint
     |
     v
vLLM
```

Exact compatibility depends on the client and protocol supported by the selected agent.

## 6. Backend Profiles

Backend-specific configuration should be isolated into environment profiles.

Example:

```text
profiles/
├── baseline.env
├── vllm.env
└── ollama.env
```

Example values:

```bash
OPENAI_BASE_URL=http://gpu-server:8000/v1
OPENAI_API_KEY=demo
MODEL_NAME=Qwen/Qwen3-8B
```

Switching backend should require as little application change as possible.

## 7. Deployment Topology

The preferred demo topology is a two-machine setup.

```text
Developer Laptop
      |
      | HTTP
      |
      v
GPU Server
+----------------------+
| vLLM / Ollama        |
|                      |
| LLM                  |
| GPU                  |
+----------------------+
```

This setup demonstrates that the inference server is a network service rather than simply a local Python library.

## 8. Extensibility

Future serving backends can be added under `servers/`:

```text
servers/
├── vllm/
├── ollama/
├── sglang/
├── tgi/
├── llama-cpp/
└── baseline-fastapi/
```

As long as the backend provides a compatible API, existing clients and benchmarks should remain reusable.
