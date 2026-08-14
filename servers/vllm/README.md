# vLLM Server

The vLLM serving backend exposes the main optimized OpenAI-compatible
endpoint of the lab via `vllm serve`. See [docs/04 §3](../docs/04-project-technical-stack.md)
for the role vLLM plays in the project.

## Prerequisites

vLLM requires a Linux server with an NVIDIA GPU. Before starting the server,
make sure the GPU server has:

- **Linux** — vLLM does not support Windows or macOS hosts.
- **An NVIDIA GPU** (e.g. A100, V100, RTX 4090, ...) with enough VRAM to hold
  the chosen model (see `MODEL_NAME` in the configuration).
- **A compatible NVIDIA driver** for the GPU.
- **A CUDA environment** required by the installed vLLM release (vLLM ships
  CUDA-specific wheels; install the one matching your driver/CUDA version).
- **vLLM installed** — e.g. `pip install vllm`, or the official vLLM Docker
  image.

The developer machine only sends HTTP requests to this server; it does not
need a GPU (docs/04 §12).

## Configuration

1. Copy the template to `config.env`:

   ```bash
   cp servers/vllm/config.env.example servers/vllm/config.env
   ```

2. Edit `servers/vllm/config.env` as needed:

   | Variable             | Default       | Meaning                              |
   |----------------------|---------------|--------------------------------------|
   | `MODEL_NAME`         | `Qwen/Qwen3-8B` | Model to serve                     |
   | `HOST`               | `0.0.0.0`     | Bind address (keep `0.0.0.0` for LAN) |
   | `PORT`               | `8000`        | OpenAI-compatible endpoint port      |
   | `TENSOR_PARALLEL_SIZE` | `1`         | GPUs across which the model is sharded |

## Start the server

From the repo root:

```bash
bash servers/vllm/run.sh
```

Or launch vLLM directly with the same options:

```bash
vllm serve "$MODEL_NAME" --host 0.0.0.0 --port 8000
```

The server exposes the OpenAI-compatible API at
`http://<host>:8000/v1` (e.g. `POST /v1/chat/completions`). Clients configured
with `OPENAI_BASE_URL=http://<host>:8000/v1` and `MODEL_NAME` can talk to it
backend-neutrally (see `profiles/vllm.env`).

## Smoke test

```bash
curl http://localhost:8000/v1/models
```

A successful response lists the served model and confirms the endpoint is up.
