# 05 - Running Cookbook

How to run this lab: start a serving backend (server side), point the clients
or benchmarks at it (client side), and verify everything works. Every piece is
**backend-neutral** — the same client code runs unchanged against vLLM, Ollama,
or the baseline FastAPI server because all of them speak an OpenAI-compatible
API (docs 02 §6, docs 03 §2.5).

## 1. When do you need environment variables?

**Only on the client side.** The three variables below are what clients and
benchmarks read from the shell. The **servers do not need them** — each server
runner (`servers/*/run.sh`) sources its own config internally, so you just run
the script directly (section 2).

| Variable | Meaning |
|---|---|
| `OPENAI_BASE_URL` | OpenAI-compatible API base URL, **including the `/v1` suffix** |
| `OPENAI_API_KEY` | API key (self-hosted backends usually accept any value, e.g. `demo`) |
| `MODEL_NAME` | Model served by the selected backend |

Ready-made per-backend sets live in `profiles/<backend>.env` (they point at the
GPU server host). **On the developer machine**, load the profile for the
backend you want to talk to:

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

**No environment setup required.** Each runner sources its own profile and
config internally (bind host, port, model) — you only run one command. The
runner also **pre-downloads the model** to the server's Hugging Face (vLLM,
baseline) or Ollama cache before serving, so the first request never triggers a
download. Export `MODEL_NAME` beforehand to choose which model is downloaded
and served, e.g. `export MODEL_NAME=Qwen/Qwen3.5-2B`.

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
The baseline implements **only** `POST /v1/chat/completions` (no `/v1/models`),
in both non-streaming and streaming (`stream: true`, SSE) forms — so all three
benchmarks work against it.

### 2.2 vLLM (GPU, primary backend)

The main optimized serving engine (docs 04 §3). Requires a **Linux server with
an NVIDIA GPU** and vLLM installed. The developer machine only sends HTTP
requests; it needs no GPU.

**Install vLLM** (one-time, on the GPU server, into the project venv so
`run.sh` finds it):

```bash
# on the GPU server
cd ~/llm-serving-lab
uv pip install --python .venv/bin/python vllm
```

Requirements:

- Linux + NVIDIA GPU + a compatible NVIDIA driver (e.g. driver 580.x / CUDA 13).
- A host compiler compatible with the CUDA toolkit: **CUDA 13 requires GCC ≤ 12**.
  `run.sh` already routes nvcc/host compilers to `/usr/bin/gcc-12` when present.
- Enough disk space for the vLLM package plus the model weights (~5-8 GB).
- `huggingface_hub` for the pre-download step (a `transformers`/vLLM dependency).

**Start** (the runner pre-downloads the model, then serves):

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
`GET /v1/models`). The **first start JIT-compiles kernels and can take a few
minutes** before the API answers — poll `curl http://localhost:8000/v1/models`
rather than assuming a crash.

### 2.3 Ollama (CPU, alternative backend)

Shows backend interchangeability with a lightweight engine running on the same
server box as vLLM (docs 04 §5). CPU-friendly; requires
[Ollama](https://ollama.com/download) installed on the server.

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
(`MODEL_NAME=qwen3.5:2b`).

### 2.4 Quick reference

| Backend | Prereq | Config file | Start command | Default endpoint |
|---|---|---|---|---|
| Baseline FastAPI | GPU server, pinned pip deps | `profiles/baseline.env` | `bash servers/baseline-fastapi/run.sh` | bind `0.0.0.0:8080`; client URL `http://192.168.30.244:8080/v1` |
| vLLM | Linux + NVIDIA GPU + vLLM | `servers/vllm/config.env` | `bash servers/vllm/run.sh` | bind `0.0.0.0:8000`; client URL `http://192.168.30.244:8000/v1` |
| Ollama | Ollama installed | `servers/ollama/Modelfile` | `bash servers/ollama/run.sh` | bind `0.0.0.0:11434`; client URL `http://192.168.30.244:11434/v1` |

> **Note on the Makefile:** `make serve-baseline|serve-vllm|serve-ollama`
> currently only print the effective `OPENAI_BASE_URL` / `MODEL_NAME`; they do
> **not** launch the backend. Use the `run.sh` scripts above to actually start
> a server. The `smoke` / `benchmark` / `health` Makefile targets are likewise
> placeholders for Sprints 5-7 and do not execute yet.

---

## 3. Client side: consuming a backend

All clients read the env contract from section 1. In the shell where you run a
client, source the matching profile (or export the three vars), then run any
client unchanged against any backend.

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

See [06 - Benchmark Running Cookbook](06-benchmark-running-cookbook.md) for the
dedicated, step-by-step benchmark guide (order, options, results, reading the
metrics). Summary below.

Lightweight, backend-neutral benchmarks (docs 04 §9; not a scientific study,
docs 03 §2.6). They are **clients**: like the clients above, they need the env
contract in the shell — source a profile first. Run with `uv run`; deps are
resolved per script.

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

> The streaming benchmarks need a backend that supports `stream: true`. All
> three backends (vLLM, Ollama, baseline FastAPI) now do.

---

## 5. End-to-end walkthrough

### 5.1 Against a server backend (vLLM or Ollama)

```bash
# 1. start the backend (on the server box) — no env setup needed
bash servers/vllm/run.sh              # or bash servers/ollama/run.sh

# 2. on the developer machine, load the matching profile (client side)
set -a; source profiles/vllm.env; set +a

# 3. verify it is up (uses the profile's OPENAI_BASE_URL)
curl $OPENAI_BASE_URL/models

# 4. consume it
uv run clients/openai-sdk/chat_completions.py
uv run benchmarks/single_request.py
```

### 5.2 Against the remote GPU server

Your real setup: a GPU box at `192.168.30.244` running all three backends —
vLLM, Ollama, and the baseline FastAPI (the baseline must live on the GPU
server because it loads the model with Transformers + torch). Model
`Qwen/Qwen3.5-2B`. The client env contract is the only thing that differs per
backend; every other command is identical.

On the server box, start a backend directly (no env setup):

```bash
# on the GPU server
bash servers/vllm/run.sh              # vLLM  -> port 8000
bash servers/ollama/run.sh            # Ollama -> port 11434
bash servers/baseline-fastapi/run.sh  # baseline -> port 8080
```

On the developer machine, set the env contract for the backend you want, then
consume/benchmark it:

```powershell
# PowerShell (client machine) — values from profiles/vllm.env
$env:OPENAI_BASE_URL = "http://192.168.30.244:8000/v1"
$env:OPENAI_API_KEY  = "demo"
$env:MODEL_NAME      = "Qwen/Qwen3.5-2B"

# verify reachability
curl $env:OPENAI_BASE_URL/models

# consume + benchmark
uv run clients/openai-sdk/chat_completions.py
uv run benchmarks/latency.py --iterations 10
uv run benchmarks/concurrency.py --requests 16 --concurrency 4
```

To switch to another backend, re-export `OPENAI_BASE_URL` (and `MODEL_NAME` if
the backend uses a different tag, e.g. Ollama's `qwen3.5:2b`): vLLM → port
`8000`, Ollama → port `11434`, baseline → port `8080`. The same clients and
benchmarks work unchanged against all three backends. In bash, `set -a;
source profiles/<backend>.env; set +a` loads the values for you.

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
- **vLLM: engine init fails with `unsupported GNU version` / `_Float32 is undefined`**
  — CUDA 13's nvcc rejects host GCC newer than 12 while flashinfer JIT-compiles
  its kernels at first start. `servers/vllm/run.sh` handles this by exporting
  `CC=/usr/bin/gcc-12`, `CXX=/usr/bin/g++-12`, and
  `NVCC_PREPEND_FLAGS="-ccbin=/usr/bin/g++-12"`. If you run `vllm serve`
  manually on a CUDA 13 box, export those three variables yourself. (`-allow-unsupported-compiler`
  alone is not enough.)
- **vLLM: API is not answering right after launch** — the first start
  JIT-compiles flashinfer ops and can take minutes; poll
  `curl http://localhost:8000/v1/models` before concluding it crashed.
- **`pip install vllm` fails / disk full** — vLLM plus model weights need
  several GB; check with `df -h /` and free space first. Installing vLLM into
  the shared project venv also pins its `torch` version, which the baseline
  backend shares — keep the two in one venv or use separate environments if a
  torch conflict arises.
