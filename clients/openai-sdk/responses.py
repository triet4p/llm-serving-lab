#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "openai>=1.0",
# ]
# ///
"""Backend-neutral Responses API client using the OpenAI SDK.

Reads the shared configuration contract OPENAI_BASE_URL / OPENAI_API_KEY /
MODEL_NAME (see .env.example and configs/models.env) so the same code works
against any OpenAI-compatible backend that exposes the Responses API
(docs 04 §7). Protocol support is a per-backend capability: not every backend
implements POST /v1/responses yet (e.g. the baseline FastAPI server does not).

Usage:

    uv run clients/openai-sdk/responses.py
"""

import os

from openai import OpenAI


def main() -> None:
    client = OpenAI(
        base_url=os.environ["OPENAI_BASE_URL"],
        api_key=os.environ["OPENAI_API_KEY"],
    )
    response = client.responses.create(
        model=os.environ["MODEL_NAME"],
        input="Explain in one sentence what an LLM serving engine does.",
        max_output_tokens=128,
    )
    print(response.output_text)


if __name__ == "__main__":
    main()
