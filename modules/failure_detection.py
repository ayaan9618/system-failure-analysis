FAILURE_KEYWORDS = (
    "error",
    "failed",
    "exception",
    "fatal",
    "rollback",
    "unable to",
    "could not",
)

RECOVERY_KEYWORDS = (
    "rollback completed",
    "recovered",
    "recovery completed",
    "service restored",
    "completed successfully",
    "deployment successful",
    "build completed",
)


def detect_failure(parsed_logs):
    """
    Return the detected incident start and end timestamps.
    """

    incident = detect_failure_details(parsed_logs)
    return incident["failure_start"], incident["failure_end"]


def detect_failure_details(parsed_logs):
    """
    Detect incident boundaries and capture the supporting timeline.
    """

    failure_start = None
    failure_end = None
    timeline = []
    incident_active = False
    last_failure_timestamp = None
    recovered = False

    for log in parsed_logs:
        message = log["message"].lower()
        is_failure_event = _is_failure_event(log, message)
        is_recovery_event = _is_recovery_event(message)

        if is_failure_event and failure_start is None:
            failure_start = log["timestamp"]
            incident_active = True

        if incident_active:
            timeline.append(log)

        if is_failure_event:
            last_failure_timestamp = log["timestamp"]

        if incident_active and is_recovery_event:
            failure_end = log["timestamp"]
            recovered = True
            break

    if failure_start and failure_end is None:
        failure_end = last_failure_timestamp

    if failure_start and not timeline and last_failure_timestamp:
        timeline = [
            log for log in parsed_logs
            if failure_start <= log["timestamp"] <= last_failure_timestamp
        ]

    return {
        "failure_start": failure_start,
        "failure_end": failure_end,
        "timeline": timeline,
        "timeline_summary": summarize_timeline(timeline),
        "status": _determine_status(failure_start, failure_end, recovered),
    }


def summarize_timeline(timeline):
    """
    Create a compact incident timeline for reporting.
    """

    summary = []

    for log in timeline:
        summary.append(
            {
                "timestamp": log.get("timestamp"),
                "level": log.get("level"),
                "message": log.get("message"),
            }
        )

    return summary


def _is_failure_event(log, message):
    if log.get("level") == "ERROR":
        return True

    return any(keyword in message for keyword in FAILURE_KEYWORDS)


def _is_recovery_event(message):
    return any(keyword in message for keyword in RECOVERY_KEYWORDS)


def _determine_status(failure_start, failure_end, recovered):
    if failure_start is None:
        return "no_failure_detected"

    if not recovered:
        return "failure_detected_no_recovery"

    return "recovered"
