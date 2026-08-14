# Project Concept / Overview

## 1. Purpose

This project is a hands-on playground for demonstrating how Large Language Models (LLMs) can be served and consumed through different inference backends.

The primary focus is **vLLM**, with additional backends such as **Ollama** and a **Python + FastAPI baseline** included for comparison.

The project is designed for software engineers who are familiar with backend systems, APIs, and application development, but may not have deep experience with AI infrastructure or LLM inference.

## 2. Core Idea

The project separates the system into two independent concerns:

- **Model Serving** — how an LLM is hosted and exposed over the network.
- **Model Consumption** — how applications, SDKs, scripts, benchmarks, and agents communicate with the model.

This separation allows the same client code to communicate with different serving backends whenever they expose a compatible API.

Conceptually:

```text
                     Application / Client
                              |
                              |
                    OpenAI-compatible API
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
           vLLM          Ollama        Baseline FastAPI
              |               |               |
              +---------------+---------------+
                              |
                             LLM
```

## 3. Main Goals

The project aims to demonstrate:

1. How an LLM can be served using plain Python and FastAPI.
2. How vLLM simplifies LLM serving compared with a custom implementation.
3. How OpenAI-compatible APIs reduce coupling between applications and inference backends.
4. How the same client can switch between vLLM, Ollama, or another compatible backend.
5. How serving systems behave under single-request and concurrent workloads.
6. How a self-hosted LLM endpoint can be integrated with real developer tools or agents.

## 4. Intended Audience

The primary audience is software engineers who:

- understand HTTP APIs;
- have experience with Python or backend development;
- understand basic deployment concepts;
- may not understand LLM inference internals;
- want to learn how self-hosted LLM serving works.

The project intentionally avoids requiring deep knowledge of:

- model training;
- CUDA kernel development;
- distributed training;
- transformer mathematics;
- ML research workflows.

## 5. Key Learning Story

The project follows a progressive learning path:

```text
model.generate()
      |
      v
Python + FastAPI
      |
      v
Dedicated LLM Serving
      |
      v
vLLM
      |
      v
OpenAI-compatible API
      |
      v
Applications / SDKs / Agents
```

The main takeaway is that **LLM serving is an infrastructure problem separate from application logic**.

An application should ideally depend on a stable API contract rather than a specific serving engine.

## 6. Why vLLM

vLLM is the central backend in this project because it provides a production-oriented LLM serving engine with features such as:

- efficient request scheduling;
- continuous batching;
- optimized KV-cache management;
- high-throughput inference;
- OpenAI-compatible serving APIs;
- support for modern LLM workloads such as chat and tool calling.

The project does not attempt to present vLLM as the only valid inference backend. Instead, it uses other backends to make the architectural differences visible.

## 7. Repository Philosophy

The repository should remain:

- easy to clone;
- easy to understand;
- easy to demo;
- backend-neutral at the client layer;
- small enough to use during a live technical talk;
- reusable after the presentation as a learning lab.

The repository should favor **clarity over production complexity**.

Production concerns such as full authentication infrastructure, Kubernetes deployment, autoscaling, multi-node inference, observability platforms, and production gateways may be discussed but are not required for the core demo.
