#!/usr/bin/env python3

from fair_billing import (
    time_to_seconds,
    parse_log_line,
    group_by_user,
    calculate_user_sessions,
)


def test_time_to_seconds():
    """Test time conversion function."""
    assert time_to_seconds("14:02:03") == 50523
    assert time_to_seconds("00:00:00") == 0
    assert time_to_seconds("23:59:59") == 86399
    assert time_to_seconds("01:30:45") == 5445


def test_parse_log_line_valid():
    """Test parsing valid log lines."""
    result = parse_log_line("14:02:03 ALICE99 Start")
    assert result == (50523, "ALICE99", "Start")

    result = parse_log_line("14:02:05 CHARLIE End")
    assert result == (50525, "CHARLIE", "End")


def test_parse_log_line_invalid():
    """Test parsing invalid log lines."""
    assert parse_log_line("invalid log line") is None
    assert parse_log_line("14:02:03 ALICE99") is None
    assert parse_log_line("14:02:03 ALICE99 Invalid") is None
    assert parse_log_line("") is None


def test_group_by_user():
    """Test grouping entries by user."""
    entries = [
        (50523, "ALICE99", "Start"),
        (50525, "CHARLIE", "End"),
        (50554, "ALICE99", "End"),
    ]
    result = group_by_user(entries)
    expected = {
        "ALICE99": [(50523, "Start"), (50554, "End")],
        "CHARLIE": [(50525, "End")],
    }
    assert result == expected


def test_calculate_user_sessions_simple():
    """Test simple session calculation."""
    events = [(50523, "Start"), (50554, "End")]
    sessions, total_time = calculate_user_sessions(events, 50523, 50554)
    assert sessions == 1
    assert total_time == 31  # 50554 - 50523


def test_calculate_user_sessions_unmatched_end():
    """Test session with unmatched End (no Start)."""
    events = [(50554, "End")]
    sessions, total_time = calculate_user_sessions(events, 50523, 50554)
    assert sessions == 1
    assert total_time == 31  # 50554 - 50523 (earliest)


def test_calculate_user_sessions_unmatched_start():
    """Test session with unmatched Start (no End)."""
    events = [(50523, "Start")]
    sessions, total_time = calculate_user_sessions(events, 50523, 50554)
    assert sessions == 1
    assert total_time == 31  # 50554 - 50523 (latest)


def test_calculate_user_sessions():
    """Test multiple overlapping sessions."""
    events = [
        (50523, "Start"),  # ALICE99 Start
        (50554, "End"),  # ALICE99 End (matches with 50523)
        (50578, "Start"),  # ALICE99 Start
        (50613, "Start"),  # ALICE99 Start
        (50615, "End"),  # ALICE99 End (matches with 50613)
        (50645, "End"),  # ALICE99 End (matches with 50578)
        (50663, "End"),  # ALICE99 End (no Start, uses earliest)
    ]
    sessions, total_time = calculate_user_sessions(events, 50523, 50681)
    assert sessions == 4
    assert total_time == 240
