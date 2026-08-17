import json
import os
import threading
import time
import uuid

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer

app = FastAPI(title="Baseline FastAPI Server")

MODEL_NAME = os.environ.get("MODEL_NAME", "Qwen/Qwen3.5-2B")

_model = None
_tokenizer = None


def load_model():
    global _model, _tokenizer
    if _model is None or _tokenizer is None:
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    return _tokenizer, _model


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = MODEL_NAME
    messages: list[ChatMessage]
    max_tokens: int = 128
    temperature: float = 0.7
    stream: bool = False


def _prepare_inputs(tokenizer, request):
    messages = [message.model_dump() for message in request.messages]
    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt",
    )
    if not hasattr(inputs, "input_ids") and not isinstance(inputs, dict):
        inputs = {"input_ids": inputs}
    return inputs


def _generation_kwargs(request) -> dict:
    return {
        "max_new_tokens": request.max_tokens,
        "temperature": request.temperature,
        "do_sample": request.temperature > 0,
    }


@app.post("/v1/chat/completions")
def chat_completions(request: ChatCompletionRequest):
    if request.stream:
        return _stream_chat_completions(request)
    return _chat_completions(request)


def _chat_completions(request: ChatCompletionRequest) -> dict:
    tokenizer, model = load_model()
    inputs = _prepare_inputs(tokenizer, request)
    outputs = model.generate(**inputs, **_generation_kwargs(request))
    generated = outputs[0][inputs["input_ids"].shape[1] :]
    content = tokenizer.decode(generated, skip_special_tokens=True)

    return {
        "id": f"chatcmpl-{uuid.uuid4().hex}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
    }


def _stream_chat_completions(request: ChatCompletionRequest) -> StreamingResponse:
    tokenizer, model = load_model()
    inputs = _prepare_inputs(tokenizer, request)
    streamer = TextIteratorStreamer(
        tokenizer, skip_prompt=True, skip_special_tokens=True
    )
    kwargs = {
        **inputs,
        **_generation_kwargs(request),
        "streamer": streamer,
    }
    thread = threading.Thread(target=model.generate, kwargs=kwargs)
    thread.start()

    def generate():
        for text in streamer:
            chunk = {
                "id": f"chatcmpl-{uuid.uuid4().hex}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": request.model,
                "choices": [
                    {"index": 0, "delta": {"content": text}, "finish_reason": None}
                ],
            }
            yield f"data: {json.dumps(chunk)}\n\n"
        done = {
            "id": f"chatcmpl-{uuid.uuid4().hex}",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": request.model,
            "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
        }
        yield f"data: {json.dumps(done)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
