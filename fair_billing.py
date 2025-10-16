#!/usr/bin/env python3
import sys


def time_to_seconds(time_str):
    """Convert HH:MM:SS to total seconds."""
    hours, minutes, seconds = map(int, time_str.split(":"))
    return hours * 3600 + minutes * 60 + seconds


def parse_log_line(line):
    """
    Parse a log line and return Tuple (time, user, action) or None if invalid.
    """
    parts = line.strip().split()
    if len(parts) == 3:
        time_str, user, action = parts
        if action in ["Start", "End"] and ":" in time_str:
            try:
                time_seconds = time_to_seconds(time_str)
                return (time_seconds, user, action)
            except ValueError:
                pass
    return None


def read_log_entries(filename):
    """Read and parse all valid entries from log file."""
    entries = []
    with open(filename, "r") as file:
        for line in file:
            entry = parse_log_line(line)
            if entry:
                entries.append(entry)
    return entries


def group_by_user(entries):
    """Group log entries by username."""
    user_data = {}
    for time, user, action in entries:
        if user not in user_data:
            user_data[user] = []
        user_data[user].append((time, action))
    return user_data


def calculate_user_sessions(events, earliest_time, latest_time):
    """Calculate sessions and billing for a single user."""
    # Separate starts and ends
    starts = []
    ends = []
    for time, action in events:
        if action == "Start":
            starts.append(time)
        else:
            ends.append(time)
    sessions = 0
    total_time = 0

    # Match each End with a Start
    for end_time in ends:
        sessions += 1

        # Find the latest Start before this End
        matched_start = None
        latest_valid_start = None
        for i, start_time in enumerate(starts):
            if start_time <= end_time:
                if latest_valid_start is None or start_time > latest_valid_start:
                    matched_start = i
                    latest_valid_start = start_time

        if matched_start is not None:

            start_time = starts.pop(matched_start)

            total_time += end_time - start_time
        else:
            total_time += end_time - earliest_time

    # Handle leftover Starts
    for start_time in starts:
        sessions += 1
        total_time += latest_time - start_time
    return sessions, total_time


def calculate_billing(filename):
    """Read log file and calculate billing for each user."""
    entries = read_log_entries(filename)
    if not entries:
        return {}

    earliest_time = min(entry[0] for entry in entries)
    latest_time = max(entry[0] for entry in entries)

    user_data = group_by_user(entries)

    results = {}
    for user, events in user_data.items():
        sessions, total_time = calculate_user_sessions(
            events, earliest_time, latest_time
        )
        results[user] = (sessions, total_time)

    return results


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fair_billing.py <logfile>")
        exit()

    results = calculate_billing(sys.argv[1])
    for user in sorted(results.keys()):
        sessions, total_time = results[user]
        print(f"{user} {sessions} {total_time}")
