import time
from unittest.mock import MagicMock

from app.log_collector import LogCollector


def _make_collector():
    api = MagicMock()
    api.send_step_logs = MagicMock(return_value=True)
    return LogCollector(api, "step-123"), api


def test_stop_collecting_flushes_buffered_logs():
    collector, api = _make_collector()
    collector.logs_buffer = [("line 1", "stdout"), ("line 2", "stdout")]
    collector.stop_collecting()
    api.send_step_logs.assert_called_once_with(
        "step-123", [("line 1", "stdout"), ("line 2", "stdout")], start_line=1
    )


def test_stop_collecting_does_not_call_api_if_buffer_empty():
    collector, api = _make_collector()
    collector.stop_collecting()
    api.send_step_logs.assert_not_called()


def test_flush_clears_buffer():
    collector, api = _make_collector()
    collector.logs_buffer = [("a", "stdout"), ("b", "stderr"), ("c", "stdout")]
    collector._flush_logs()
    assert collector.logs_buffer == []


def test_flush_sends_correct_step_id():
    collector, api = _make_collector()
    collector.logs_buffer = [("hello", "stdout")]
    collector._flush_logs()
    api.send_step_logs.assert_called_once_with(
        "step-123", [("hello", "stdout")], start_line=1
    )


def test_flush_preserves_stderr_stream():
    collector, api = _make_collector()
    collector.logs_buffer = [("warning: deprecated", "stderr")]
    collector._flush_logs()
    api.send_step_logs.assert_called_once_with(
        "step-123", [("warning: deprecated", "stderr")], start_line=1
    )


def test_batch_flush_when_buffer_reaches_limit():
    collector, api = _make_collector()
    for i in range(collector.batch_size):
        with collector._lock:
            collector.logs_buffer.append((f"line {i}", "stdout"))
            if len(collector.logs_buffer) >= collector.batch_size:
                collector._flush_logs()
    api.send_step_logs.assert_called_once()
    assert collector.logs_buffer == []
