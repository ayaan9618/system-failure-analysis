from datetime import datetime


def calculate_downtime(start, end, status=None):
    """
    Calculate downtime metrics for an incident window.
    """

    start_time = _ensure_datetime(start)
    end_time = _ensure_datetime(end)

    if start_time is None:
        return {
            "start_time": None,
            "end_time": None,
            "duration": None,
            "duration_seconds": None,
            "duration_minutes": None,
            "status": status or "no_failure_detected",
            "is_recovered": False,
        }

    normalized_status = status or "unknown"

    if end_time is None:
        return {
            "start_time": start_time,
            "end_time": None,
            "duration": None,
            "duration_seconds": None,
            "duration_minutes": None,
            "status": normalized_status if normalized_status != "unknown" else "failure_detected_no_recovery",
            "is_recovered": False,
        }

    duration = end_time - start_time
    duration_seconds = int(duration.total_seconds())
    duration_minutes = round(duration_seconds / 60, 2)

    return {
        "start_time": start_time,
        "end_time": end_time,
        "duration": duration,
        "duration_seconds": duration_seconds,
        "duration_minutes": duration_minutes,
        "status": normalized_status if normalized_status != "unknown" else "recovered",
        "is_recovered": normalized_status == "recovered",
    }


def format_downtime(downtime_details):
    """
    Convert downtime metrics into a display-friendly string.
    """

    if not downtime_details or downtime_details.get("duration") is None:
        if downtime_details and downtime_details.get("start_time") is not None:
            return "Ongoing incident - recovery not detected"
        return "Not available"

    return str(downtime_details["duration"])


def _ensure_datetime(value):
    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
