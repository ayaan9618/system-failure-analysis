import json
import re
from pathlib import Path
from xml.etree import ElementTree

#clf file reformat
CLF_PATTERN = re.compile(
    r'^(?P<host>\S+) \S+ \S+ \[(?P<timestamp>[^\]]+)\] '
    r'"(?P<action>[^"]+)" (?P<status>\d{3}) "(?P<message>.*)"$'
)
#log file reformat
RAW_LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\S+)\t(?P<message>.*)$"
)

#load
def load_logs(file_path):
    """
    Load logs from supported file formats and return raw records.
    """

    path = Path(file_path)
    suffix = path.suffix.lower()

    # check file extension
    if suffix == ".json":
        return _load_json(path)
    if suffix in {".yaml", ".yml"}:
        return _load_yaml(path)
    if suffix == ".xml":
        return _load_xml(path)
    if suffix == ".clf":
        return _load_clf(path)
    if suffix == ".elf":
        return _load_elf(path)
    if suffix == ".log":
        return _load_raw_log(path)

    raise ValueError(f"Unsupported log format: {suffix}")

# json
def _load_json(path):
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("JSON logs must be a list of log records")

    return data


def _load_yaml(path):
    records = []
    current = {}

    with path.open("r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.rstrip()

            if not line.strip():
                continue

            if line.startswith("- "):
                if current:
                    records.append(current)
                current = {}
                line = line[2:]

            key, value = _split_key_value(line)
            current[key] = _clean_scalar(value)

    if current:
        records.append(current)

    return records


def _load_xml(path):
    root = ElementTree.parse(path).getroot()
    records = []

    for node in root.findall("log"):
        records.append(
            {
                "timestamp": _node_text(node.find("timestamp")),
                "level": _node_text(node.find("level")),
                "message": _node_text(node.find("message")),
            }
        )

    return records


def _load_clf(path):
    records = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            match = CLF_PATTERN.match(line.strip())
            if not match:
                continue

            status_code = int(match.group("status"))
            records.append(
                {
                    "timestamp": match.group("timestamp"),
                    "level": _status_to_level(status_code),
                    "message": match.group("message"),
                    "source_action": match.group("action"),
                    "status_code": status_code,
                }
            )

    return records


def _load_elf(path):
    records = []

    with path.open("r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line or line.startswith("#Fields:"):
                continue

            parts = line.split(" ", 3)
            if len(parts) != 4:
                continue

            date, time, level, message = parts
            records.append(
                {
                    "timestamp": f"{date}T{time}Z",
                    "level": level,
                    "message": _clean_scalar(message),
                }
            )

    return records


def _load_raw_log(path):
    records = []

    with path.open("r", encoding="utf-8", errors="replace") as file:
        for raw_line in file:
            line = raw_line.rstrip("\n")
            if not line.strip():
                continue

            match = RAW_LOG_PATTERN.match(line)
            if not match:
                continue

            message = match.group("message").strip()
            if not message:
                continue

            records.append(
                {
                    "timestamp": match.group("timestamp"),
                    "level": _infer_level_from_message(message),
                    "message": message,
                }
            )

    return records


def _split_key_value(line):
    if ":" not in line:
        raise ValueError(f"Invalid YAML line: {line}")

    key, value = line.split(":", 1)
    return key.strip(), value.strip()


def _clean_scalar(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return value[1:-1]
    if len(value) >= 2 and value[0] == "'" and value[-1] == "'":
        return value[1:-1]
    return value


def _node_text(node):
    if node is None or node.text is None:
        return ""
    return node.text.strip()


def _status_to_level(status_code):
    if status_code >= 500:
        return "ERROR"
    if status_code >= 400:
        return "WARNING"
    return "INFO"


def _infer_level_from_message(message):
    lowered = message.lower()

    if any(token in lowered for token in ["error", "failed", "exception"]):
        return "ERROR"
    if any(token in lowered for token in ["warn", "deprecated"]):
        return "WARNING"
    return "INFO"
