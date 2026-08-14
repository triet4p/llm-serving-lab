import os
import time
import uuid

from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer

app = FastAPI(title="Baseline FastAPI Server")

MODEL_NAME = os.environ.get("MODEL_NAME", "Qwen/Qwen3-8B")

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


@app.post("/v1/chat/completions")
def chat_completions(request: ChatCompletionRequest):
    tokenizer, model = load_model()

    messages = [message.model_dump() for message in request.messages]
    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt",
    )
    outputs = model.generate(
        inputs,
        max_new_tokens=request.max_tokens,
        temperature=request.temperature,
        do_sample=request.temperature > 0,
    )
    generated = outputs[0][inputs.shape[1] :]
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
