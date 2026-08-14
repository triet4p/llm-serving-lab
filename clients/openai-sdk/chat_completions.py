#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "openai>=1.0",
# ]
# ///
"""Backend-neutral chat completion client using the OpenAI SDK.

Reads the shared configuration contract OPENAI_BASE_URL / OPENAI_API_KEY /
MODEL_NAME (see .env.example and configs/models.env) so the same code works
against any OpenAI-compatible backend: vLLM, Ollama, or the baseline FastAPI
server (docs 03 §2.5).

Usage:

    uv run clients/openai-sdk/chat_completions.py
"""

import os

from openai import OpenAI


def main() -> None:
    client = OpenAI(
        base_url=os.environ["OPENAI_BASE_URL"],
        api_key=os.environ["OPENAI_API_KEY"],
    )
    completion = client.chat.completions.create(
        model=os.environ["MODEL_NAME"],
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Explain in one sentence what an LLM serving engine does."},
        ],
        max_tokens=128,
        temperature=0.7,
    )
    print(completion.choices[0].message.content)


if __name__ == "__main__":
    main()
