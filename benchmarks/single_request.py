#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "httpx>=0.27",
# ]
# ///
"""Backend-neutral single-request benchmark.

Sends one streaming chat completion to any OpenAI-compatible backend and
reports the raw timings a demo audience cares about:

    total latency        wall time of the whole request
    time-to-first-token  wall time until the first content token arrives
    generation time      first token -> end of stream
    tokens               number of content chunks received
    tokens/sec           tokens / generation time

Reads the shared configuration contract OPENAI_BASE_URL / OPENAI_API_KEY /
MODEL_NAME (see .env.example and configs/models.env), so the same script works
against vLLM, Ollama, or the baseline FastAPI server (docs 03 §2.5). The
benchmark is intentionally lightweight (Python + httpx + monotonic timers,
docs 04 §9) and is not a scientific study (docs 03 §2.6).

Usage:

    uv run benchmarks/single_request.py
    uv run benchmarks/single_request.py --prompt "Hello!"
    uv run benchmarks/single_request.py --no-save

Results are written as JSON and CSV into `benchmarks/results/` unless
`--no-save` is given.
"""

import argparse
import csv
import json
import os
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


def load_dataset(name: str) -> list[dict]:
    """Load a benchmark dataset (benchmarks/datasets/<name>.json)."""
    path = Path(__file__).resolve().parent / "datasets" / f"{name}.json"
    if not path.is_file():
        raise SystemExit(f"Dataset not found: {name!r}. Expected at {path}.")
    return json.loads(path.read_text(encoding="utf-8"))["requests"]


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


def save_results(
    script_name: str, summary: dict, rows: list[dict], output_dir: str | None = None
) -> tuple[Path, Path]:
    """Write JSON + CSV results into the output dir and return their paths."""
    results_dir = (
        Path(output_dir)
        if output_dir
        else Path(__file__).resolve().parent / "results"
    )
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
    parser = argparse.ArgumentParser(description="Single-request latency benchmark")
    parser.add_argument(
        "--prompt",
        default="Explain in one sentence what an LLM serving engine does.",
        help="user prompt to send (default: a one-sentence explanation prompt)",
    )
    parser.add_argument("--max-tokens", type=int, default=128, help="max_tokens for the request")
    parser.add_argument(
        "--dataset",
        default=None,
        help="benchmark dataset name (benchmarks/datasets/<name>.json); overrides --prompt",
    )
    parser.add_argument(
        "--label",
        default=None,
        help="only pick the dataset request with this label (e.g. short, long)",
    )
    parser.add_argument(
        "--thinking",
        choices=["auto", "on", "off"],
        default="auto",
        help="send chat_template_kwargs enable_thinking (on/off) or none (auto)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=0,
        help="per-request timeout in seconds (0 = no timeout)",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="directory to write JSON/CSV results into (default: benchmarks/results/)",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="skip writing JSON/CSV results to benchmarks/results/",
    )
    args = parser.parse_args()

    base_url = required_env("OPENAI_BASE_URL").rstrip("/")
    api_key = required_env("OPENAI_API_KEY")
    model = required_env("MODEL_NAME")

    if args.dataset:
        entries = load_dataset(args.dataset)
        if args.label:
            entries = [e for e in entries if e.get("label") == args.label]
            if not entries:
                raise SystemExit(f"No dataset request with label {args.label!r} in {args.dataset}")
        entry = entries[0]
        prompt = entry["prompt"]
        max_tokens = entry.get("max_tokens", args.max_tokens)
        entry_label = entry.get("label", "")
    else:
        prompt = args.prompt
        max_tokens = args.max_tokens
        entry_label = ""

    url = f"{base_url}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "stream": True,
    }
    if args.thinking != "auto":
        payload["chat_template_kwargs"] = {"enable_thinking": args.thinking == "on"}

    with httpx.Client(timeout=args.timeout or None) as client:
        result = send_request(client, url, headers, payload)
    if entry_label:
        result["label"] = entry_label

    print(f"model:      {model}")
    print(f"endpoint:   {url}")
    if entry_label:
        print(f"request:    label={entry_label} max_tokens={max_tokens}")
    print("---")
    print(f"total latency (s):        {result['total_time']:.3f}")
    print(f"time-to-first-token (s):  {result['time_to_first_token']:.3f}")
    print(f"generation time (s):      {result['generation_time']:.3f}")
    print(f"tokens:                   {result['tokens']}")
    print(f"tokens/sec:               {result['tokens_per_second']:.1f}")

    if not args.no_save:
        json_path, csv_path = save_results("single_request", result, [result], args.output_dir)
        print(f"saved:                    {json_path}")
        print(f"saved:                    {csv_path}")


if __name__ == "__main__":
    main()
