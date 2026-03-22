from datetime import datetime


def calculate_downtime(start, end):
    start_time = _ensure_datetime(start)
    end_time = _ensure_datetime(end)

    downtime = end_time - start_time

    return downtime


def _ensure_datetime(value):
    if isinstance(value, datetime):
        return value

    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
