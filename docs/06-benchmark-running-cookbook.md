# 06 - Benchmark Running Cookbook

How to run the benchmarks against a serving backend. Benchmarks are **clients**:
like the clients in [05 - Running Cookbook](05-running-cookbook.md), they need
the env contract in the shell where they run — the servers do not (each runner
sources its own config internally).

This document also includes the **continuous batching demo** (section 8): a
mixed short/long dataset that shows the profit of vLLM's continuous batching
over the serialized baseline FastAPI server.

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
for total latency, TTFT, and generation time. With `--dataset` it cycles through
the dataset and prints a per-label summary.

```powershell
uv run benchmarks/latency.py --iterations 10
```

### 3.3 Throughput — concurrent requests

Fires a batch of requests in parallel (`--concurrency` bounds concurrency with
a semaphore) and reports wall time, requests/sec, and tokens/sec. With
`--dataset` the batch cycles through the dataset (section 8 uses this).

```powershell
uv run benchmarks/concurrency.py --requests 8 --concurrency 4
```

Start with a small concurrency (e.g. 4) and increase to see how the backend
behaves under load.

## 4. Datasets (swapping workloads)

Benchmarks read their requests from a **dataset**: a JSON file in
`benchmarks/datasets/`. Two ship with the repo:

- `default.json` — the original single-prompt benchmark (one-sentence
  explanation prompt, `max_tokens=1024`). Equivalent to running without
  `--dataset`.
- `multi-length.json` — a short/medium/long mix used by the continuous batching
  demo (section 8).

Use one with `--dataset <name>` on any benchmark script:

```powershell
uv run benchmarks/concurrency.py --dataset multi-length --requests 6 --concurrency 3
```

**Swap or add a dataset** — no code changes needed:

- Add `benchmarks/datasets/<name>.json` with the shape
  `{"name", "description", "requests": [{"label"?, "prompt", "max_tokens"?}]}`.
- `max_tokens` is optional per entry (falls back to `--max-tokens`).
- `label` groups entries in the `per-label summary`.
- `single_request.py` also accepts `--label short|long` to pick one entry.

## 5. Results

Every run writes two files into `benchmarks/results/` (gitignored):

- `<name>_<timestamp>.json` — full detail: summary + per-request rows.
- `<name>_<timestamp>.csv` — one row per request (metrics as columns).

Add `--no-save` to print only and skip writing files. Use `--output-dir <path>`
to save results somewhere else (e.g. keep each option/session's results
separate).

### 5.1 Aggregation report

`benchmarks/aggregate_report.py` turns a results directory into a per-type
markdown report: one section for each of the three benchmark types
(`single_request`, `latency`, `concurrency`), a table with one run per row plus
an **aggregate (mean)** row, and — when the runs used a dataset with multiple
prompts — a **per-label** table (short/medium/long ...) built from every
per-request row.

```powershell
uv run benchmarks/aggregate_report.py                                    # default: benchmarks/results/
uv run benchmarks/aggregate_report.py --results-dir results/multi-length  # a specific dir
uv run benchmarks/aggregate_report.py --output report.md                  # also write the report
```

It works for any dataset because each saved JSON carries its per-request rows
with their `label`.

## 6. Options reference

| Script | Flag | Default | Meaning |
|---|---|---|---|
| all | `--no-save` | off | skip writing JSON/CSV results |
| all | `--prompt` | one-sentence explanation | user prompt to send (ignored with `--dataset`) |
| all | `--max-tokens` | 128 | `max_tokens` per request (fallback when a dataset entry omits it) |
| all | `--dataset` | none | load requests from `benchmarks/datasets/<name>.json` (`default`, `multi-length`, or your own) |
| all | `--thinking` | `auto` | `chat_template_kwargs.enable_thinking`: `on`/`off` forces it, `auto` sends nothing |
| all | `--timeout` | 0 | per-request timeout in seconds (`0` = no timeout; raise it for slow backends / long reasoning) |
| all | `--output-dir` | `benchmarks/results/` | directory to write JSON/CSV results into |
| `single_request.py` | `--label` | none | with `--dataset`, only pick the request with this label (e.g. `short`) |
| `latency.py` | `--iterations` | 10 | number of requests to run (cycles through the dataset) |
| `concurrency.py` | `--requests` | 8 | total requests to fire (cycles through the dataset) |
| `concurrency.py` | `--concurrency` | 4 | requests in parallel |

## 7. Reading the metrics

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

## 8. Continuous batching demo (multi-length dataset)

### 8.1 Why this demo

A serving engine that only processes one request at a time (like the baseline
FastAPI server) makes a long request **block every short request behind it**:
total time ≈ the *sum* of all request times.

vLLM implements **continuous batching**: it schedules generation **token by
token**, so a long request and several short requests run in the *same batch*.
Short requests finish quickly in the gaps between the long request's tokens;
total time ≈ the *longest* single request. This is the core efficiency win
(docs 04 §3).

### 8.2 The dataset

`benchmarks/datasets/multi-length.json`:

| label | max_tokens | example prompt |
|---|---|---|
| short | 16–32 | "Hi.", "What is 2+2?" |
| medium | 128–256 | "Explain in one sentence what an LLM serving engine does." |
| long | 1024 | "Write a detailed essay explaining how continuous batching …" |

### 8.3 How to run

Start one backend on the GPU server (foreground), then the other for
comparison:

```bash
# vLLM (8000) — the engine with continuous batching
export MODEL_NAME=Qwen/Qwen3.5-2B && bash servers/vllm/run.sh

# Baseline (8081) — serialized, for comparison (stop vLLM first)
export PORT=8081 MODEL_NAME=Qwen/Qwen3.5-2B && bash servers/baseline-fastapi/run.sh
```

Poll readiness: `curl localhost:<port>/v1/models` (vLLM) / log
"Application startup complete" (baseline).

Fire the whole dataset once, concurrently, on the dev machine:

```powershell
$env:OPENAI_API_KEY = "demo"
$env:OPENAI_BASE_URL = "http://192.168.30.244:8000/v1"   # or :8081 for baseline
$env:MODEL_NAME     = "Qwen/Qwen3.5-2B"

uv run benchmarks/concurrency.py --dataset multi-length --requests 6 --concurrency 3 --thinking off
```

Repeat with `OPENAI_BASE_URL` pointing at the other backend. Use
`--requests 12 --concurrency 6` for a stronger effect (the dataset cycles).
Optionally see per-label numbers:

```powershell
uv run benchmarks/latency.py --dataset multi-length --iterations 6 --thinking off
```

### 8.4 Reading the results — the "proof"

Compare the two backends' **wall time** for the *same* dataset and the *same*
concurrency level:

- **vLLM** — all requests start together; short ones finish while the long one
  is still generating. Expect `wall time ≈` the longest request (seconds) and
  `requests/sec` ≈ `requests / longest_request`.
- **Baseline** — requests run one after another. Expect `wall time ≈` the sum
  of every request's latency (minutes) and per-label latency growing with
  queue position (short requests wait behind the long ones).

| expected | vLLM | Baseline |
|---|---|---|
| wall time (6 req, conc 3) | ~longest request | ~sum of all |
| short-request latency | low, stable | high, grows with queue |
| requests/sec | high | low |
| tokens/sec | high | low |

> Use `--thinking off` for a clean comparison (Ollama always reasons and is
> left out of the thinking-off runs). The qualitative batching effect holds
> either way.

## 9. Backend notes

- All three backends (vLLM, Ollama, baseline FastAPI) accept the streaming
  requests the benchmarks send.
- The baseline implements only `/v1/chat/completions` (no `/v1/models`), so the
  `curl $OPENAI_BASE_URL/models` check in section 2 fails against it; reach it
  with `chat_completions.py` instead.
- The benchmark scripts send chat completions; switch backends by re-pointing
  `OPENAI_BASE_URL` (and `MODEL_NAME`) as in section 2.

## 10. Troubleshooting

- **`Missing required env var 'OPENAI_BASE_URL' ...`** — the env contract is
  not set in this shell; source a profile or export the three vars (section 2).
- **Connection refused / timeout** — the backend is not running, or
  `OPENAI_BASE_URL` does not match the backend's port/bind; verify with
  `curl $env:OPENAI_BASE_URL/models`.
- **`Dataset not found: ...`** — the JSON is not in `benchmarks/datasets/` or
  the name is misspelled (section 4).
- **`uv run` is slow the first time** — it resolves the script's inline
  dependencies once; subsequent runs reuse the cached environment.
