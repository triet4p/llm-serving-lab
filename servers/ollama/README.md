# Ollama Server

The Ollama serving backend exposes an alternative OpenAI-compatible endpoint
to demonstrate backend interchangeability. It is not intended to compete with
vLLM on throughput; its role is to show that the client layer stays unchanged
across serving implementations (docs/02 §4.3, docs/04 §5).

## Prerequisites

- **Ollama installed** — download from <https://ollama.com/download> for
  Linux, macOS, or Windows. Ollama runs on CPU, so **no GPU is required**.
- **`curl`** for the smoke test.

The developer machine only sends HTTP requests to the server; Ollama itself
runs on the same server box as the other backends. No GPU is needed for this
backend (Ollama is CPU-friendly).

## Configuration

The model and its serving parameters live in `servers/ollama/Modelfile`:

| Setting      | Default   | Meaning                              |
|--------------|-----------|--------------------------------------|
| `FROM`       | `qwen3.5:2b` | Base model the created model derives from |
| `num_ctx`    | `4096`    | Context window size in tokens         |
| `temperature`| `0.7`     | Default sampling temperature          |
| `num_predict`| `2048`    | Maximum tokens generated per request  |

The model tag created from the Modelfile matches `MODEL_NAME` in
`profiles/ollama.env` (`qwen3.5:2b`), so clients address it by that name. The
OpenAI-compatible base URL comes from the same profile:
`OPENAI_BASE_URL=http://192.168.30.244:11434/v1` (the server host; adjust if
your server's address differs).

Optional overrides (export before running):

| Variable       | Default           | Meaning                    |
|----------------|-------------------|----------------------------|
| `OLLAMA_HOST`  | `0.0.0.0:11434`   | Bind address for `ollama serve` |
| `MODEL_NAME`   | `qwen3.5:2b`        | Model tag to create/serve  |

## Start the server

From the repo root:

```bash
bash servers/ollama/run.sh
```

The runner starts `ollama serve` in the background, creates the model from the
Modelfile with `ollama create "$MODEL_NAME" -f servers/ollama/Modelfile`
(skipped when the tag already exists), and keeps serving in the foreground.
The OpenAI-compatible API is exposed at
`http://<host>:11434/v1` (e.g. `POST /v1/chat/completions`). Clients configured
with `OPENAI_BASE_URL=http://<host>:11434/v1` and `MODEL_NAME` can talk to it
backend-neutrally (see `profiles/ollama.env`).

## Smoke test

```bash
curl http://localhost:11434/v1/models
```

A successful response lists the served model and confirms the endpoint is up.
