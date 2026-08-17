from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "servers" / "baseline-fastapi" / "app.py"


def app_text() -> str:
    return APP.read_text(encoding="utf-8")


def test_request_model_accepts_stream_flag():
    assert "stream: bool = False" in app_text()


def test_endpoint_branches_on_stream():
    assert "if request.stream:" in app_text()


def test_streaming_uses_text_iterator_streamer():
    assert "TextIteratorStreamer" in app_text()
    assert "threading.Thread" in app_text()


def test_streaming_returns_sse_response():
    text = app_text()
    assert "StreamingResponse" in text
    assert 'media_type="text/event-stream"' in text


def test_streaming_chunks_follow_openai_sse_format():
    text = app_text()
    assert '"object": "chat.completion.chunk"' in text
    assert "data: [DONE]" in text
    assert '"delta"' in text


def test_non_streaming_response_unchanged():
    assert '"object": "chat.completion"' in app_text()
