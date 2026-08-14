from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "servers" / "baseline-fastapi" / "app.py"


def app_text() -> str:
    return APP.read_text(encoding="utf-8")


def test_chat_completions_endpoint_registered():
    assert '@app.post("/v1/chat/completions")' in app_text()


def test_endpoint_parses_request_body():
    assert "ChatCompletionRequest" in app_text()


def test_endpoint_calls_tokenizer():
    assert "apply_chat_template" in app_text()


def test_endpoint_calls_model_generate():
    assert "model.generate(" in app_text()


def test_endpoint_serializes_response():
    assert '"object": "chat.completion"' in app_text()
    assert '"choices"' in app_text()
    assert '"message"' in app_text()
    assert '"content"' in app_text()


def test_endpoint_decodes_output():
    assert "tokenizer.decode" in app_text()
