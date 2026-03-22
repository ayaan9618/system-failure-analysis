from pathlib import Path


def generate_report(
    incident_details,
    downtime,
    error_analysis,
    root_cause,
    output_path="output/reports/system_failure_report.txt",
):
    """
    Generate a structured text incident report.
    """

    failure_start = incident_details.get("failure_start")
    failure_end = incident_details.get("failure_end")
    status = incident_details.get("status", "unknown")
    timeline_summary = incident_details.get("timeline_summary", [])

    total_errors = error_analysis.get("total_errors", 0)
    error_counts = error_analysis.get("error_counts", {})
    top_modules = error_analysis.get("top_affected_modules", [])

    report = "\n===== SYSTEM FAILURE REPORT =====\n\n"
    report += "Incident Overview:\n"
    report += f"Status: {status}\n"
    report += f"Failure Start Time: {failure_start}\n"
    report += f"Failure End Time: {failure_end}\n"
    report += f"Total Downtime: {_format_downtime(downtime)}\n"
    report += f"Downtime Seconds: {downtime.get('duration_seconds')}\n"
    report += f"Downtime Minutes: {downtime.get('duration_minutes')}\n\n"

    report += "Error Analysis:\n"
    report += f"Total Errors: {total_errors}\n"
    report += "Top Error Messages:\n"
    for error, count in list(error_counts.items())[:10]:
        report += f"- {error} ({count})\n"

    report += "\nAffected Modules:\n"
    if top_modules:
        for module, count in top_modules:
            report += f"- {module} ({count})\n"
    else:
        report += "- None identified\n"

    report += "\nPredicted Root Cause:\n"
    report += f"Summary: {root_cause.get('summary', 'Unknown')}\n"
    report += f"Category: {root_cause.get('category', 'unknown')}\n"
    report += f"Confidence: {root_cause.get('confidence', 'low')}\n"
    report += "Evidence:\n"
    for evidence_item in root_cause.get("evidence", []):
        report += f"- {evidence_item}\n"

    report += "\nIncident Timeline Summary:\n"
    if timeline_summary:
        for item in timeline_summary[:15]:
            report += (
                f"- {item['timestamp']} | {item['level']} | {item['message']}\n"
            )
    else:
        report += "- No incident timeline available\n"

    file_path = Path(output_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as file:
        file.write(report)

    return report, str(file_path)


def _format_downtime(downtime):
    duration = downtime.get("duration")
    if duration is None:
        if downtime.get("start_time") is not None:
            return "Ongoing incident - recovery not detected"
        return "Not available"
    return str(duration)
