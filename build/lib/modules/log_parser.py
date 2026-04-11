from datetime import datetime
import re


SUPPORTED_TIMESTAMP_FORMATS = (
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S.%fZ",
)

ANSI_ESCAPE_PATTERN = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")


def parse_logs(logs):
    """
    Validate and normalize raw log records for downstream analysis.
    """

    parsed_logs = []

    for index, log in enumerate(logs, start=1):
        timestamp = _parse_timestamp(log.get("timestamp"), index)
        level = _normalize_level(log.get("level", "INFO"))
        message = _normalize_message(log.get("message"), index)
        if message is None:
            continue

        parsed_log = {
            "timestamp": timestamp,
            "level": level,
            "message": message,
            "timestamp_raw": log.get("timestamp"),
        }

        for extra_key, extra_value in log.items():
            if extra_key not in parsed_log:
                parsed_log[extra_key] = extra_value

        parsed_logs.append(parsed_log)

    parsed_logs.sort(key=lambda log: log["timestamp"])

    return parsed_logs


def _parse_timestamp(value, index):
    if not value:
        raise ValueError(f"Missing timestamp in log record {index}")

    for fmt in SUPPORTED_TIMESTAMP_FORMATS:
        try:
            return datetime.strptime(str(value), fmt)
        except ValueError:
            continue

    raise ValueError(
        f"Unsupported timestamp format in log record {index}: {value}"
    )


def _normalize_level(value):
    normalized = str(value).strip().upper()
    if not normalized:
        return "INFO"
    return normalized


def _normalize_message(value, index):
    message = str(value).strip() if value is not None else ""
    message = ANSI_ESCAPE_PATTERN.sub("", message)
    message = message.encode("ascii", "ignore").decode("ascii")
    message = message.strip()
    if not message:
        return None
    return message
