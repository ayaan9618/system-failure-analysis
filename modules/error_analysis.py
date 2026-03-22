from collections import Counter
import re


MODULE_RESOLUTION_PATTERN = re.compile(
    r'could not resolve(?: module)?\s+(?:"|\')?(?P<module>[^"\']+)(?:"|\')?',
    re.IGNORECASE,
)


def analyze_errors(parsed_logs):
    """
    Analyze error patterns from normalized logs.
    """

    error_messages = []
    normalized_error_messages = []
    affected_modules = []

    for log in parsed_logs:
        if log["level"] != "ERROR":
            continue

        message = log["message"]
        error_messages.append(message)
        normalized_error_messages.append(_normalize_error_message(message))

        module_name = _extract_module_name(message)
        if module_name:
            affected_modules.append(module_name)

    error_count = Counter(error_messages)
    normalized_error_count = Counter(normalized_error_messages)
    module_count = Counter(affected_modules)
    total_errors = len(error_messages)

    return {
        "total_errors": total_errors,
        "error_counts": error_count,
        "normalized_error_counts": normalized_error_count,
        "affected_modules": module_count,
        "top_errors": error_count.most_common(5),
        "top_error_patterns": normalized_error_count.most_common(5),
        "top_affected_modules": module_count.most_common(10),
    }


def _normalize_error_message(message):
    normalized = message.strip()
    normalized = re.sub(r"^\[ERROR\]\s*", "", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r'"[^"]+"', '"<module>"', normalized)
    normalized = re.sub(r"'[^']+'", "'<module>'", normalized)
    normalized = re.sub(r"\b\d+\b", "<number>", normalized)
    return normalized


def _extract_module_name(message):
    match = MODULE_RESOLUTION_PATTERN.search(message)
    if match:
        return match.group("module").strip()
    return None
