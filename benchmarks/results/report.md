# Benchmark Aggregation Report
- results dir: C:\Users\admin\Desktop\Workspace\llm-serving-lab\benchmarks\results
- generated: 2026-08-17 16:24:44

## default

### single_request

| backend | runs | total_s | ttft_s | gen_s | tokens | tok_s |
|---|---|---|---|---|---|---|
| baseline | 1 | 24.990 | 5.452 | 19.538 | 767.000 | 39.256 |
| ollama | 1 | 14.530 | 3.934 | 10.596 | 907.000 | 85.595 |
| vllm | 1 | 15.085 | 0.122 | 14.963 | 1024.000 | 68.434 |

### latency

| backend | runs | mean_total_s | p50_total_s | p95_total_s | mean_ttft_s | tokens_mean |
|---|---|---|---|---|---|---|
| baseline | 1 | 19.844 | 19.677 | 20.517 | 0.120 | 801.000 |
| ollama | 1 | 10.748 | 10.740 | 10.767 | 0.157 | 895.000 |
| vllm | 1 | 15.017 | 15.014 | 15.031 | 0.052 | 1024.000 |

### concurrency

| backend | runs | wall_s | req_s | tok_s | lat_mean_s |
|---|---|---|---|---|---|
| baseline | 1 | 381.387 | 0.052 | 41.446 | 55.269 |
| ollama | 2 | 212.042 | 0.094 | 84.101 | 30.185 |
| vllm | 1 | 110.450 | 0.181 | 185.423 | 15.757 |

## multi-length

### concurrency

| backend | runs | wall_s | req_s | tok_s | lat_mean_s |
|---|---|---|---|---|---|
| baseline | 1 | 362.260 | 0.055 | 37.407 | 48.062 |
| ollama | 1 | 219.154 | 0.091 | 81.185 | 32.671 |
| vllm | 1 | 127.254 | 0.157 | 154.502 | 15.135 |

#### by label

| backend | label | n | mean_total_s | mean_ttft_s | mean_tokens |
|---|---|---|---|---|---|
| baseline | long | 3 | 173.112 | 0.378 | 2762.333 |
| baseline | medium | 6 | 58.016 | 0.273 | 732.667 |
| baseline | short | 11 | 8.528 | 2.276 | 78.909 |
| ollama | long | 3 | 68.681 | 21.318 | 3764.000 |
| ollama | medium | 6 | 17.984 | 7.357 | 917.167 |
| ollama | short | 11 | 30.862 | 29.725 | 90.636 |
| vllm | long | 3 | 62.739 | 0.056 | 4096.000 |
| vllm | medium | 6 | 15.817 | 0.059 | 1024.000 |
| vllm | short | 11 | 1.780 | 0.063 | 111.727 |

