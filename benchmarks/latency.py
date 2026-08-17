#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "httpx>=0.27",
# ]
# ///
"""Backend-neutral latency benchmark.

Runs repeated streaming chat completions against any OpenAI-compatible
backend and aggregates latency statistics across all requests. Reports, for
both total latency and time-to-first-token:

    min / max / mean   basic spread
    p50 / p90 / p95    percentile latency (the typical case)

Reads the shared configuration contract OPENAI_BASE_URL / OPENAI_API_KEY /
MODEL_NAME (see .env.example and configs/models.env), so the same script works
against vLLM, Ollama, or the baseline FastAPI server (docs 03 §2.5). The
benchmark is intentionally lightweight (Python + httpx + monotonic timers,
docs 04 §9) and is not a scientific study (docs 03 §2.6).

Usage:

    uv run benchmarks/latency.py
    uv run benchmarks/latency.py --iterations 20
    uv run benchmarks/latency.py --no-save

Results are written as JSON and CSV into `benchmarks/results/` unless
`--no-save` is given.
"""

import argparse
import csv
import json
import os
import statistics
import time
from pathlib import Path

import httpx


def required_env(name: str) -> str:
    try:
        return os.environ[name]
    except KeyError:
        raise SystemExit(
            f"Missing required env var {name!r}. Set OPENAI_BASE_URL / "
            "OPENAI_API_KEY / MODEL_NAME (see .env.example and configs/models.env)."
        )


def send_request(client: httpx.Client, url: str, headers: dict, payload: dict) -> dict:
    """Stream one chat completion and time it with a monotonic clock."""
    start = time.perf_counter()
    first_token_time: float | None = None
    tokens = 0
    with client.stream("POST", url, headers=headers, json=payload) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if not line or not line.startswith("data:"):
                continue
            chunk = line[5:].strip()
            if chunk == "[DONE]":
                break
            try:
                obj = json.loads(chunk)
            except json.JSONDecodeError:
                continue
            choices = obj.get("choices") or []
            if not choices:
                continue
            delta = choices[0].get("delta") or {}
            text = (
                delta.get("content")
                or delta.get("reasoning")
                or delta.get("reasoning_content")
                or ""
            )
            if text:
                tokens += 1
                if first_token_time is None:
                    first_token_time = time.perf_counter() - start
    total = time.perf_counter() - start
    ttft = first_token_time if first_token_time is not None else total
    generation = max(total - ttft, 0.0)
    return {
        "total_time": total,
        "time_to_first_token": ttft,
        "generation_time": generation,
        "tokens": tokens,
        "tokens_per_second": tokens / generation if generation > 0 else 0.0,
    }


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, int(p / 100.0 * len(ordered)))
    return ordered[index]


def summarize(values: list[float]) -> dict:
    return {
        "min": min(values) if values else 0.0,
        "max": max(values) if values else 0.0,
        "mean": statistics.fmean(values) if values else 0.0,
        "p50": percentile(values, 50),
        "p90": percentile(values, 90),
        "p95": percentile(values, 95),
    }


def save_results(script_name: str, summary: dict, rows: list[dict]) -> tuple[Path, Path]:
    """Write JSON + CSV results into benchmarks/results/ and return their paths."""
    results_dir = Path(__file__).resolve().parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    base = results_dir / f"{script_name}_{timestamp}"
    json_path = base.with_suffix(".json")
    csv_path = base.with_suffix(".csv")
    json_path.write_text(
        json.dumps({"summary": summary, "requests": rows}, indent=2),
        encoding="utf-8",
    )
    if rows:
        fieldnames = list(rows[0].keys())
        with csv_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    return json_path, csv_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Repeated-request latency benchmark")
    parser.add_argument(
        "--iterations",
        type=int,
        default=10,
        help="number of requests to run (default: 10)",
    )
    parser.add_argument(
        "--prompt",
        default="Explain in one sentence what an LLM serving engine does.",
        help="user prompt to send (default: a one-sentence explanation prompt)",
    )
    parser.add_argument("--max-tokens", type=int, default=128, help="max_tokens for each request")
    parser.add_argument(
        "--thinking",
        choices=["auto", "on", "off"],
        default="auto",
        help="send chat_template_kwargs enable_thinking (on/off) or none (auto)",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="skip writing JSON/CSV results to benchmarks/results/",
    )
    args = parser.parse_args()

    if args.iterations < 1:
        raise SystemExit("--iterations must be >= 1")

    base_url = required_env("OPENAI_BASE_URL").rstrip("/")
    api_key = required_env("OPENAI_API_KEY")
    model = required_env("MODEL_NAME")

    url = f"{base_url}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": args.prompt},
        ],
        "max_tokens": args.max_tokens,
        "temperature": 0.7,
        "stream": True,
    }
    if args.thinking != "auto":
        payload["chat_template_kwargs"] = {"enable_thinking": args.thinking == "on"}

    results = []
    with httpx.Client(timeout=120.0) as client:
        for i in range(args.iterations):
            results.append(send_request(client, url, headers, payload))
            print(f"  request {i + 1}/{args.iterations} done", end="\r")
    print()

    total = [r["total_time"] for r in results]
    ttft = [r["time_to_first_token"] for r in results]
    gen = [r["generation_time"] for r in results]
    tokens = [r["tokens"] for r in results]

    print(f"model:            {model}")
    print(f"endpoint:         {url}")
    print(f"iterations:       {args.iterations}")
    print()
    print("latency summary (s)")
    for metric, values in (("total latency", total), ("time-to-first-token", ttft), ("generation", gen)):
        s = summarize(values)
        print(
            f"  {metric:>20}: min={s['min']:.3f} max={s['max']:.3f} "
            f"mean={s['mean']:.3f} p50={s['p50']:.3f} p90={s['p90']:.3f} p95={s['p95']:.3f}"
        )
    print(f"  {'tokens':>20}: mean={statistics.fmean(tokens):.1f}")

    if not args.no_save:
        summary = {
            "model": model,
            "endpoint": url,
            "iterations": args.iterations,
            "total_latency_s": summarize(total),
            "time_to_first_token_s": summarize(ttft),
            "generation_time_s": summarize(gen),
            "tokens_mean": statistics.fmean(tokens),
        }
        json_path, csv_path = save_results("latency", summary, results)
        print(f"saved:  {json_path}")
        print(f"saved:  {csv_path}")


if __name__ == "__main__":
    main()
