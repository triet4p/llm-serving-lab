from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = [
    ROOT / "benchmarks" / "single_request.py",
    ROOT / "benchmarks" / "latency.py",
    ROOT / "benchmarks" / "concurrency.py",
]
APP = ROOT / "servers" / "baseline-fastapi" / "app.py"


def test_benchmarks_offer_thinking_flag():
    for script in SCRIPTS:
        text = script.read_text(encoding="utf-8")
        assert script.is_file(), f"{script.name} must exist"
        assert "--thinking" in text
        assert "enable_thinking" in text
        assert 'args.thinking == "on"' in text


def test_benchmarks_offer_configurable_timeout():
    for script in SCRIPTS:
        text = script.read_text(encoding="utf-8")
        assert "--timeout" in text
        assert "0 = no timeout" in text
        assert "timeout or None" in text


def test_benchmarks_send_chat_template_kwargs_only_when_forced():
    for script in SCRIPTS:
        text = script.read_text(encoding="utf-8")
        assert 'if args.thinking != "auto":' in text
        assert 'payload["chat_template_kwargs"]' in text


def test_baseline_accepts_chat_template_kwargs():
    text = APP.read_text(encoding="utf-8")
    assert "chat_template_kwargs: dict | None = None" in text
    assert "template_kwargs = request.chat_template_kwargs or {}" in text
    assert "**template_kwargs" in text
