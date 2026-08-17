# 05 - Running Cookbook

How to run this lab: start a serving backend (server side), point the clients
or benchmarks at it (client side), and verify everything works. Every piece is
**backend-neutral** — the same client code runs unchanged against vLLM, Ollama,
or the baseline FastAPI server because all of them speak an OpenAI-compatible
API (docs 02 §6, docs 03 §2.5).

## 1. The configuration contract

Servers, clients, and benchmarks all read the same three environment
variables:

| Variable | Meaning |
|---|---|
| `OPENAI_BASE_URL` | OpenAI-compatible API base URL, **including the `/v1` suffix** |
| `OPENAI_API_KEY` | API key (self-hosted backends usually accept any value, e.g. `demo`) |
| `MODEL_NAME` | Model served by the selected backend |

Sources, in increasing precedence:

1. `configs/models.env` — default model (the fallback `MODEL_NAME`).
2. `profiles/<backend>.env` — a complete per-backend set of all three vars.
3. Your shell / `.env` — anything you export wins.

**To point everything at a backend**, export the three variables (or source a
profile):

```bash
# pick a backend profile (bash)
set -a; source profiles/vllm.env; set +a

# or export manually
export OPENAI_BASE_URL=http://192.168.30.244:8000/v1
export OPENAI_API_KEY=demo
export MODEL_NAME=Qwen/Qwen3.5-2B
```

```powershell
# PowerShell equivalent
$env:OPENAI_BASE_URL = "http://192.168.30.244:8000/v1"
$env:OPENAI_API_KEY  = "demo"
$env:MODEL_NAME      = "Qwen/Qwen3.5-2B"
```

> **Platform note:** the backend runners (`servers/*/run.sh`) and the Makefile
> are bash scripts and need WSL or Git Bash on Windows. The clients and
> benchmarks are cross-platform (curl / `uv run`).

---

## 2. Server side: running a backend

### 2.1 Baseline FastAPI (educational)

A hand-written FastAPI server that loads the model with Hugging Face
Transformers and exposes `POST /v1/chat/completions` (docs 04 §4).

> **Run it on the GPU server.** The baseline loads the model with
> Transformers + torch, so it runs on the **same GPU server as vLLM** — not on
> the developer machine. The runner binds `0.0.0.0` so the developer machine
> can reach it over the network.

```bash
# on the GPU SERVER: one-time install of pinned deps
pip install -r servers/baseline-fastapi/requirements.txt

# on the GPU SERVER: start (defaults: 0.0.0.0:8080, MODEL_NAME from profiles/baseline.env)
bash servers/baseline-fastapi/run.sh

# override port / host if needed
PORT=9090 HOST=0.0.0.0 bash servers/baseline-fastapi/run.sh
```

Endpoint on the GPU server: `http://0.0.0.0:8080/v1`; clients on the developer
machine reach it at `http://192.168.30.244:8080/v1` (per `profiles/baseline.env`).
The baseline implements **only** `POST /v1/chat/completions` (non-streaming) —
no `/v1/models`, no streaming, so the streaming benchmarks are not usable
against it.

### 2.2 vLLM (GPU, primary backend)

The main optimized serving engine (docs 04 §3). Requires a **Linux server with
an NVIDIA GPU** and vLLM installed (`pip install vllm` or the vLLM Docker
image). The developer machine only sends HTTP requests; it needs no GPU.

```bash
# one-time: configure the server (model, host, port, tensor-parallel size)
cp servers/vllm/config.env.example servers/vllm/config.env
# edit servers/vllm/config.env as needed

# start
bash servers/vllm/run.sh
```

The runner sources `configs/models.env` + `profiles/vllm.env`, overrides them
with `servers/vllm/config.env` when present, then launches:

```bash
vllm serve "$MODEL_NAME" --host 0.0.0.0 --port "$PORT" --tensor-parallel-size "$TENSOR_PARALLEL_SIZE"
```

Endpoint: `http://<host>:8000/v1` (e.g. `POST /v1/chat/completions`,
`GET /v1/models`).

### 2.3 Ollama (CPU, alternative backend)

Shows backend interchangeability with a lightweight local engine (docs 04 §5).
CPU only; requires [Ollama](https://ollama.com/download) installed.

```bash
# start: launches the daemon, creates the model from the Modelfile
# (skipped when the tag already exists), keeps serving in the foreground
bash servers/ollama/run.sh
```

Equivalent of what the runner does:

```bash
ollama serve &                       # background daemon
ollama create "$MODEL_NAME" -f servers/ollama/Modelfile   # once per tag
wait                                  # keep serving
```

Endpoint: `http://<host>:11434/v1` (e.g. `POST /v1/chat/completions`,
`GET /v1/models`). Model tag comes from `profiles/ollama.env`
(`MODEL_NAME=qwen3:8b`).

### 2.4 Quick reference

| Backend | Prereq | Config file | Start command | Default endpoint |
|---|---|---|---|---|
| Baseline FastAPI | GPU server, pinned pip deps | `profiles/baseline.env` | `bash servers/baseline-fastapi/run.sh` | `http://0.0.0.0:8080/v1` (client URL `http://192.168.30.244:8080/v1`) |
| vLLM | Linux + NVIDIA GPU + vLLM | `servers/vllm/config.env` | `bash servers/vllm/run.sh` | `http://0.0.0.0:8000/v1` |
| Ollama | Ollama installed | `servers/ollama/Modelfile` | `bash servers/ollama/run.sh` | `http://0.0.0.0:11434/v1` |

> **Note on the Makefile:** `make serve-baseline|serve-vllm|serve-ollama`
> currently only print the effective `OPENAI_BASE_URL` / `MODEL_NAME`; they do
> **not** launch the backend. Use the `run.sh` scripts above to actually start
> a server. The `smoke` / `benchmark` / `health` Makefile targets are likewise
> placeholders for Sprints 5-7 and do not execute yet.

---

## 3. Client side: consuming a backend

All clients read the env contract from section 1. Set the three variables (or
source a profile), then run any client unchanged against any backend.

### 3.1 Raw HTTP with curl (`clients/raw-http/`)

```bash
set -a; source profiles/vllm.env; set +a          # or export the 3 vars

# Chat Completions (the common compatibility layer)
bash clients/raw-http/curl-chat.sh

# Responses API (only where the backend supports it)
bash clients/raw-http/curl-responses.sh
```

### 3.2 OpenAI SDK (`clients/openai-sdk/`)

Standalone scripts with inline dependencies — no `pip install` needed, run
with `uv run`:

```bash
# Chat Completions
uv run clients/openai-sdk/chat_completions.py

# legacy prompt-based Completions (where supported)
uv run clients/openai-sdk/completions.py

# Responses API (where supported)
uv run clients/openai-sdk/responses.py
```

### 3.3 Protocol capability matrix

Protocol support is a **per-backend capability**, not universal (docs 04 §7).
Which client to use:

| Client | Endpoint | Baseline | vLLM | Ollama |
|---|---|---|---|---|
| `curl-chat.sh`, `chat_completions.py` | `/v1/chat/completions` | yes | yes | yes |
| `completions.py` | `/v1/completions` | no | yes* | yes* |
| `curl-responses.sh`, `responses.py` | `/v1/responses` | no | recent versions | no* |

\* Capability depends on the installed backend version; check the backend's
docs. When in doubt, use the Chat Completions clients — that endpoint is the
common denominator across all three backends.

---

## 4. Benchmarks (`benchmarks/`)

Lightweight, backend-neutral benchmarks (docs 04 §9; not a scientific study,
docs 03 §2.6). Run with `uv run`; deps are resolved per script. Set the same
three env vars as for clients.

```bash
# single request: total latency, time-to-first-token, generation time, tokens
uv run benchmarks/single_request.py

# repeated requests: min/max/mean/p50/p90/p95 latency
uv run benchmarks/latency.py --iterations 10

# concurrency: requests/sec, tokens/sec under parallel load
uv run benchmarks/concurrency.py --requests 8 --concurrency 4
```

Every run writes `<name>_<timestamp>.json` and `.csv` into
`benchmarks/results/` (gitignored). Add `--no-save` to print only; `--help`
lists every option.

> The streaming benchmarks need a backend that supports `stream: true`.
> vLLM and Ollama do; the baseline FastAPI server does not.

---

## 5. End-to-end walkthrough

### 5.1 Against a local backend (vLLM or Ollama)

```bash
# 1. start the backend
bash servers/vllm/run.sh              # or bash servers/ollama/run.sh

# 2. in another terminal, point at it
set -a; source profiles/vllm.env; set +a

# 3. verify it is up
curl http://localhost:8000/v1/models

# 4. consume it
uv run clients/openai-sdk/chat_completions.py
uv run benchmarks/single_request.py
```

### 5.2 Against the remote GPU server

Your real setup: a GPU box at `192.168.30.244` running both the vLLM backend
**and** the baseline FastAPI server (the baseline must live on the GPU server
because it loads the model with Transformers + torch). Model
`Qwen/Qwen3.5-2B`. Only the three variables differ — the rest of the commands
are identical.

```powershell
# PowerShell (client machine)
# vLLM
$env:OPENAI_BASE_URL = "http://192.168.30.244:<PORT>/v1"   # <PORT> = vLLM port
$env:OPENAI_API_KEY  = "demo"
$env:MODEL_NAME      = "Qwen/Qwen3.5-2B"

# verify reachability
curl http://192.168.30.244:<PORT>/v1/models

# consume + benchmark
uv run clients/openai-sdk/chat_completions.py
uv run benchmarks/latency.py --iterations 10
uv run benchmarks/concurrency.py --requests 16 --concurrency 4
```

To switch to the baseline running on the same GPU server, re-export:

```powershell
$env:OPENAI_BASE_URL = "http://192.168.30.244:8080/v1"     # baseline FastAPI
# then the same clients work unchanged; only streaming benchmarks do not
# (the baseline is non-streaming)
```

---

## 6. Verification

| Check | Command | Expected |
|---|---|---|
| Backend up | `curl $OPENAI_BASE_URL/models` | JSON listing the served model |
| One-shot generation | `uv run clients/openai-sdk/chat_completions.py` | a printed completion |
| Timing | `uv run benchmarks/single_request.py` | latency / TTFT / tokens table |
| Project health | `uv run pytest -q` | all tests pass |

### Troubleshooting

- **`Missing required env var ...`** — the three variables are not set; export
  them or source a profile (section 1).
- **Connection refused** — the backend is not running, or the port/host in
  `OPENAI_BASE_URL` does not match the backend's bind address; verify with
  `curl $OPENAI_BASE_URL/models`.
- **`404` on `/v1/models`, `/v1/completions`, `/v1/responses`** — the backend
  does not implement that protocol; use the Chat Completions clients (matrix
  in §3.3).
- **`uv run` is slow the first time** — it resolves the script's inline
  dependencies once; subsequent runs reuse the cached environment.
