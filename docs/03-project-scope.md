# Project Scope

## 1. Scope Objective

The project is intended to be a compact, reproducible demonstration of LLM serving concepts for software engineers.

The scope prioritizes:

- serving architecture;
- API compatibility;
- inference backend comparison;
- client integration;
- basic performance behavior;
- developer-facing usability.

It is not intended to be a complete production LLM platform.

## 2. In Scope

### 2.1 Serving Backends

The initial version includes:

- **Python + FastAPI baseline**
- **vLLM**
- **Ollama**

The architecture should allow additional backends to be added later.

### 2.2 Model Hosting

The project should demonstrate:

- loading or serving an open-weight LLM;
- exposing the model through an HTTP endpoint;
- serving the model from a GPU server;
- querying the server remotely from another machine.

All serving backends run on the **same GPU server**; the developer machine only
sends HTTP requests to it.

### 2.3 API Interfaces

The project may demonstrate the following API styles:

- OpenAI Completions API;
- OpenAI Chat Completions API;
- OpenAI Responses API;
- Anthropic Messages API where supported or relevant.

The main focus should be API concepts and interoperability rather than exhaustive protocol coverage.

### 2.4 Client Implementations

The repository should include lightweight examples using:

- `curl`;
- raw HTTP requests where useful;
- the OpenAI Python SDK;
- selected agent or developer-tool integrations.

### 2.5 Backend Switching

The same application client should be reusable across compatible serving backends by changing configuration such as:

```text
BASE_URL
API_KEY
MODEL_NAME
```

This is one of the project's primary demonstrations.

### 2.6 Benchmarking

The project should include simple benchmarks that demonstrate serving behavior.

Possible measurements include:

- request latency;
- time to first token;
- total generation time;
- requests per second;
- tokens per second;
- concurrent request behavior.

The benchmark does not need to qualify as a comprehensive scientific performance study.

### 2.7 Demo Automation

The repository may include helper scripts for:

- starting a backend;
- checking endpoint health;
- sending smoke-test requests;
- running a small benchmark;
- switching profiles.

## 3. Primary Demo Scenarios

### Scenario 1 — Manual Baseline

Start a custom FastAPI server wrapping a model (on the GPU server).

Goal:

Show the amount of application code required when building the serving layer manually.

### Scenario 2 — vLLM Serving

Start the same or comparable model with vLLM (on the GPU server).

Goal:

Show how dedicated LLM serving infrastructure reduces custom serving code.

### Scenario 3 — Remote Client

Send requests from a developer laptop to a GPU server.

Goal:

Demonstrate the model as a remote infrastructure service.

### Scenario 4 — Same Client, Different Backend

Run the same OpenAI SDK client against multiple serving backends.

Goal:

Demonstrate protocol-level decoupling.

### Scenario 5 — Concurrent Requests

Generate multiple requests concurrently.

Goal:

Make the difference between simple inference and an optimized serving engine visible.

### Scenario 6 — Agent Integration

Point a supported agent or developer tool at a self-hosted endpoint.

Goal:

Show how model serving becomes reusable infrastructure for higher-level applications.

## 4. Out of Scope

The initial project does not aim to implement:

- LLM training;
- fine-tuning pipelines;
- RLHF;
- dataset preparation;
- distributed model training;
- production-grade authentication;
- enterprise authorization;
- billing;
- quota management;
- full observability stacks;
- Kubernetes operators;
- production autoscaling;
- multi-region deployment;
- high-availability architecture;
- advanced model routing;
- production API gateways;
- full security hardening;
- comprehensive benchmark methodology.

These topics may be mentioned as production considerations but should not dominate the demo.

## 5. Optional / Future Scope

Possible future additions include:

- SGLang;
- Hugging Face TGI;
- llama.cpp;
- multi-GPU vLLM;
- tensor parallelism demos;
- speculative decoding;
- structured outputs;
- tool calling;
- prefix caching;
- quantized models;
- Prometheus metrics;
- Grafana dashboards;
- Docker Compose;
- Kubernetes deployment;
- request routing across multiple models;
- load testing with dedicated tools;
- tracing and observability.

## 6. Success Criteria

The project can be considered successful if a developer can:

1. Clone the repository.
2. Understand the separation between client and inference server.
3. Start at least one serving backend.
4. Call it using `curl`.
5. Call it using the OpenAI SDK.
6. Change configuration and point the same client to another backend.
7. Run a simple concurrency test.
8. Understand why vLLM is useful compared with a naïve custom server.
9. Reuse the repository after the talk as a learning reference.

## 7. Scope Philosophy

The guiding principle is:

> Build enough infrastructure to expose the important engineering concepts, but not so much infrastructure that the serving concepts become hidden.

The project should remain a **teaching and experimentation repository first**.
