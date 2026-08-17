# 06 - Benchmark Running Cookbook

How to run the benchmarks against a serving backend. Benchmarks are **clients**:
like the clients in [05 - Running Cookbook](05-running-cookbook.md), they need
the env contract in the shell where they run — the servers do not (each runner
sources its own config internally).

## 1. Prerequisites

- A **serving backend running** on the GPU server (start one with its runner,
  e.g. `bash servers/vllm/run.sh`). All three backends support the streaming
  requests the benchmarks send (`stream: true`).
- **uv** on the developer machine. Benchmark dependencies (`httpx`) are
  resolved automatically per script via inline metadata — no `pip install`.

## 2. Set up the environment (client side)

On the developer machine, point at the backend you want to benchmark:

```bash
set -a; source profiles/vllm.env; set +a            # bash
```

```powershell
# PowerShell (values from profiles/vllm.env)
$env:OPENAI_BASE_URL = "http://192.168.30.244:8000/v1"
$env:OPENAI_API_KEY  = "demo"
$env:MODEL_NAME      = "Qwen/Qwen3.5-2B"
```

Verify reachability before benchmarking:

```powershell
curl $env:OPENAI_BASE_URL/models
```

Per-backend values (change `OPENAI_BASE_URL` and, for Ollama, `MODEL_NAME`):

| Backend | Port | MODEL_NAME |
|---|---|---|
| vLLM | 8000 | `Qwen/Qwen3.5-2B` |
| Ollama | 11434 | `qwen3.5:2b` |
| Baseline FastAPI | 8080 | `Qwen/Qwen3.5-2B` |

## 3. Run the benchmarks (recommended order)

Run them in the same shell where the env contract is set.

### 3.1 Sanity check — single request

One streaming request; reports total latency, time-to-first-token (TTFT),
generation time, token count, and tokens/sec.

```powershell
uv run benchmarks/single_request.py
```

### 3.2 Latency statistics — repeated requests

Runs N requests (default 10) and aggregates min / max / mean / p50 / p90 / p95
for total latency, TTFT, and generation time.

```powershell
uv run benchmarks/latency.py --iterations 10
```

### 3.3 Throughput — concurrent requests

Fires a batch of requests in parallel (`--concurrency` bounds concurrency with
a semaphore) and reports wall time, requests/sec, and tokens/sec.

```powershell
uv run benchmarks/concurrency.py --requests 8 --concurrency 4
```

Start with a small concurrency (e.g. 4) and increase to see how the backend
behaves under load.

## 4. Results

Every run writes two files into `benchmarks/results/` (gitignored):

- `<name>_<timestamp>.json` — full detail: summary + per-request rows.
- `<name>_<timestamp>.csv` — one row per request (metrics as columns).

Add `--no-save` to print only and skip writing files.

## 5. Options reference

| Script | Flag | Default | Meaning |
|---|---|---|---|
| all | `--no-save` | off | skip writing JSON/CSV results |
| all | `--prompt` | one-sentence explanation | user prompt to send (ignored with `--dataset`) |
| all | `--max-tokens` | 128 | `max_tokens` per request (fallback when a dataset entry omits it) |
| all | `--dataset` | none | load requests from `benchmarks/datasets/<name>.json` (see [07 - Continuous Batching Demo](07-continuous-batching-demo.md)) |
| all | `--thinking` | `auto` | `chat_template_kwargs.enable_thinking`: `on`/`off` forces it, `auto` sends nothing |
| all | `--timeout` | 0 | per-request timeout in seconds (`0` = no timeout; raise it for slow backends / long reasoning) |
| `single_request.py` | `--label` | none | with `--dataset`, only pick the request with this label (e.g. `short`) |
| `latency.py` | `--iterations` | 10 | number of requests to run (cycles through the dataset) |
| `concurrency.py` | `--requests` | 8 | total requests to fire (cycles through the dataset) |
| `concurrency.py` | `--concurrency` | 4 | requests in parallel |

## 6. Reading the metrics

- **Latency / total time (s)** — wall time of a whole request, including
  network round-trip from the developer machine.
- **Time to first token (s)** — time until the first content token arrives;
  a proxy for how quickly the backend starts generating.
- **Generation time (s)** — first token to end of stream.
- **Tokens/sec** — content chunks received per second of generation time
  (single/latency) or over total wall time (concurrency).
- **Requests/sec** (concurrency) — throughput under parallel load.

These numbers depend heavily on your machine, network, model, and load. The
benchmarks are **not** a scientific study (docs 03 §2.6) — use them to compare
backends *on the same setup*, not as absolute performance claims.

## 7. Backend notes

- All three backends (vLLM, Ollama, baseline FastAPI) accept the streaming
  requests the benchmarks send.
- The baseline implements only `/v1/chat/completions` (no `/v1/models`), so the
  `curl $OPENAI_BASE_URL/models` check in section 2 fails against it; reach it
  with `chat_completions.py` instead.
- The benchmark scripts send chat completions; switch backends by re-pointing
  `OPENAI_BASE_URL` (and `MODEL_NAME`) as in section 2.

## 8. Troubleshooting

- **`Missing required env var 'OPENAI_BASE_URL' ...`** — the env contract is
  not set in this shell; source a profile or export the three vars (section 2).
- **Connection refused / timeout** — the backend is not running, or
  `OPENAI_BASE_URL` does not match the backend's port/bind; verify with
  `curl $env:OPENAI_BASE_URL/models`.
- **`uv run` is slow the first time** — it resolves the script's inline
  dependencies once; subsequent runs reuse the cached environment.
