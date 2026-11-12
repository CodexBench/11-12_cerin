import json
from pathlib import Path

from codexbench.runner import analyze_agent_trace, first_attempt_duration, parse_token_usage


def test_tokens_exclude_cached_input_from_budget(tmp_path: Path) -> None:
    path = tmp_path / "events.jsonl"
    path.write_text(
        json.dumps(
            {
                "type": "turn.completed",
                "usage": {
                    "input_tokens": 100,
                    "cached_input_tokens": 70,
                    "output_tokens": 20,
                    "reasoning_output_tokens": 5,
                },
            }
        )
        + "\n"
    )
    usage = parse_token_usage(path)
    assert usage["uncached_input_tokens"] == 30
    assert usage["budget_tokens"] == 50


def test_trace_behavior_metrics(tmp_path: Path) -> None:
    path = tmp_path / "events.jsonl"
    events = [
        {"type": "item.completed", "item": {"type": "command_execution", "command": "bin/test test_x.py", "exit_code": 1, "status": "failed"}},
        {"type": "item.completed", "item": {"type": "file_change", "changes": [{"path": "a.py"}, {"path": "b.py"}]}},
        {"type": "item.completed", "item": {"type": "agent_message", "text": "done"}},
    ]
    path.write_text("".join(json.dumps(event) + "\n" for event in events))
    metrics = analyze_agent_trace(path)
    assert metrics == {
        "command_count": 1,
        "failed_command_count": 1,
        "test_command_count": 1,
        "file_change_count": 2,
        "agent_message_count": 1,
    }


def test_first_attempt_duration_survives_resume_events(tmp_path: Path) -> None:
    path = tmp_path / "events.jsonl"
    events = [
        {"phase": "run", "status": "started", "timestamp": "2026-11-12T00:00:00+00:00"},
        {"phase": "run", "status": "failed", "timestamp": "2026-11-12T00:03:20+00:00"},
        {"phase": "run", "status": "started", "timestamp": "2026-11-12T00:04:00+00:00"},
        {"phase": "run", "status": "failed", "timestamp": "2026-11-12T00:04:01+00:00"},
    ]
    path.write_text("".join(json.dumps(event) + "\n" for event in events))
    assert first_attempt_duration(path) == 200.0

