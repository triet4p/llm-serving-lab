# Sprint 6 Plan

## Sprint Goal
Add lightweight benchmarks demonstrating single-request, latency, and concurrent serving behavior.

## Atomic Tasks
Status legend: [ ] pending / [~] in progress / [x] done

- [ ] Task 1: Create `benchmarks/single_request.py` that sends one request and reports latency / time-to-first-token / total time.
- [ ] Task 2: Create `benchmarks/latency.py` that runs repeated requests and aggregates latency statistics.
- [ ] Task 3: Create `benchmarks/concurrency.py` using `asyncio` + `httpx` to measure concurrent request behavior (requests/sec, tokens/sec).
- [ ] Task 4: Add JSON/CSV result output and a `benchmarks/results/` directory.

## Notes / Blockers
- Keep benchmarking lightweight (Python + asyncio + httpx + monotonic timers) per docs 04 §9.
- Not a scientific study (docs 03 §2.6).
