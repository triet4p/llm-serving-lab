# 07 - Continuous Batching Demo (multi-length dataset)

How to demonstrate the profit of **continuous batching** in vLLM by serving a
**mixed workload of short and long requests** and comparing vLLM against the
serialized baseline FastAPI server.

## 1. Why this demo

A serving engine that only processes one request at a time (like the baseline
FastAPI server) makes a long request **block every short request behind it**:
total time ≈ the *sum* of all request times.

vLLM implements **continuous batching**: it schedules generation **token by
token**, so a long request and several short requests run in the *same batch*.
Short requests finish quickly in the gaps between the long request's tokens;
total time ≈ the *longest* single request. This is the core efficiency win
(docs 04 §3).

The `multi-length` dataset mixes short / medium / long requests so the effect
is measurable.

## 2. The dataset

`benchmarks/datasets/multi-length.json`:

| label | max_tokens | example prompt |
|---|---|---|
| short | 16–32 | "Hi.", "What is 2+2?" |
| medium | 128–256 | "Explain in one sentence what an LLM serving engine does." |
| long | 1024 | "Write a detailed essay explaining how continuous batching …" |

The benchmark scripts accept `--dataset <name>` to load
`benchmarks/datasets/<name>.json`. Without it they keep the legacy single
prompt, so **swapping datasets = adding a JSON file and passing `--dataset`**
(section 5).

## 3. How to run

### 3.1 Start one backend (GPU server, foreground)

```bash
# vLLM (8000) — the engine with continuous batching
export MODEL_NAME=Qwen/Qwen3.5-2B && bash servers/vllm/run.sh

# Baseline (8081) — serialized, for comparison (stop vLLM first)
export PORT=8081 MODEL_NAME=Qwen/Qwen3.5-2B && bash servers/baseline-fastapi/run.sh
```

Poll readiness: `curl localhost:<port>/v1/models` (vLLM) / log
"Application startup complete" (baseline).

### 3.2 Run the mixed concurrency benchmark (dev machine)

```powershell
$env:OPENAI_API_KEY = "demo"
$env:OPENAI_BASE_URL = "http://192.168.30.244:8000/v1"   # or :8081 for baseline
$env:MODEL_NAME     = "Qwen/Qwen3.5-2B"

# Fire the whole dataset once, concurrently (6 requests, 3 in parallel)
uv run benchmarks/concurrency.py --dataset multi-length --requests 6 --concurrency 3 --thinking off
```

Repeat with `OPENAI_BASE_URL` pointing at the other backend. Use
`--requests 12 --concurrency 6` for a stronger effect (the dataset cycles).

Optionally run the latency benchmark to see per-label numbers:

```powershell
uv run benchmarks/latency.py --dataset multi-length --iterations 6 --thinking off
```

## 4. Reading the results — the "proof"

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

## 5. Swapping / adding datasets

Two datasets ship with the repo under `benchmarks/datasets/`:

- `default.json` — the original single-prompt benchmark (equivalent to running
  without `--dataset`).
- `multi-length.json` — the short/medium/long mix used in this demo.

- **Add** a dataset: create `benchmarks/datasets/<name>.json` with the same
  shape (`name`, `description`, `requests: [{label?, prompt, max_tokens?}]`).
- **Use** it: `--dataset <name>` on any benchmark script.
- **Per-request options**: `max_tokens` is optional per entry (falls back to
  `--max-tokens`); `label` groups results in the `per-label summary`.
- **Single request**: `--dataset <name> --label short|long` picks one entry.

No code changes are needed to add a dataset.
