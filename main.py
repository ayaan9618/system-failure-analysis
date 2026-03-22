from pathlib import Path

from modules.log_input import load_logs
from modules.log_parser import parse_logs
from modules.failure_detection import detect_failure_details
from modules.downtime_calculator import calculate_downtime, format_downtime
from modules.error_analysis import analyze_errors
from modules.root_cause_analysis import detect_root_cause
from modules.report_generator import generate_report
from modules.charts import (
    plot_error_frequency,
    plot_log_levels,
    plot_error_timeline,
)
from modules.pdf_report_generator import generate_pdf_report


DEFAULT_LOG_PATH = "logs/cloud_failure_log.json"

# calling other file 
def run_analysis(log_path=DEFAULT_LOG_PATH):
    logs = parse_logs(load_logs(log_path))
    incident_details = detect_failure_details(logs)
    downtime = calculate_downtime(
        incident_details["failure_start"],
        incident_details["failure_end"],
        incident_details["status"],
    )
    analysis_scope = incident_details["timeline"] or logs
    error_analysis = analyze_errors(analysis_scope)
    root_cause = detect_root_cause(error_analysis)

    chart_paths = {
        "error_frequency": plot_error_frequency(error_analysis),
        "log_levels": plot_log_levels(logs),
        "error_timeline": plot_error_timeline(incident_details),
    }

    text_report = generate_report(
        incident_details,
        downtime,
        error_analysis,
        root_cause,
    )

    pdf_path = generate_pdf_report(
        incident_details,
        downtime,
        error_analysis,
        root_cause,
    )

    return {
        "log_path": log_path,
        "logs": logs,
        "incident_details": incident_details,
        "downtime": downtime,
        "error_analysis": error_analysis,
        "root_cause": root_cause,
        "text_report": text_report,
        "chart_paths": chart_paths,
        "pdf_path": pdf_path,
    }

# asking path
def prompt_for_log_path(default_path=DEFAULT_LOG_PATH):
    print("Enter the log file path to analyze.")
    print(f"Press Enter to use the default: {default_path}")

    while True:
        user_input = input("Log file path: ").strip()
        selected_path = user_input or default_path

        if Path(selected_path).exists():
            return selected_path

        print(f"File not found: {selected_path}")
        print("Please enter a valid log file path.")

#print summary
def print_summary(result):
    incident_details = result["incident_details"]
    downtime = result["downtime"]
    error_analysis = result["error_analysis"]
    root_cause = result["root_cause"]

    print("Logs loaded and parsed successfully!")
    print(f"Input File: {result['log_path']}")

    print("\n------ Failure Analysis ------")
    print("Failure Start Time:", incident_details["failure_start"])
    print("Failure End Time:", incident_details["failure_end"])
    print("Incident Status:", incident_details["status"])

    print("\n------ Downtime Report ------")
    print("Total Downtime:", format_downtime(downtime))
    print("Downtime Seconds:", downtime["duration_seconds"])
    print("Downtime Minutes:", downtime["duration_minutes"])

    print("\n------ Error Pattern Analysis ------")
    print("Total Errors:", error_analysis["total_errors"])
    print("\nTop Error Messages:")
    for error, count in error_analysis["top_errors"]:
        print(f"- {error} -> {count}")

    print("\n------ Root Cause Detection ------")
    print("Predicted Root Cause:", root_cause["summary"])
    print("Confidence:", root_cause["confidence"])
    for evidence_item in root_cause["evidence"]:
        print(f"- {evidence_item}")

    print("\n------ Output Files ------")
    print("Text report saved to: output/reports/system_failure_report.txt")

    if result["pdf_path"]:
        print(f"PDF report saved to: {result['pdf_path']}")
    else:
        print("PDF report skipped: reportlab is not installed")

    for chart_name, chart_path in result["chart_paths"].items():
        if chart_path:
            print(f"{chart_name} chart saved to: {chart_path}")
        else:
            print(f"{chart_name} chart skipped: matplotlib is not installed")


if __name__ == "__main__":
    selected_log_path = prompt_for_log_path()
    analysis_result = run_analysis(selected_log_path)
    print_summary(analysis_result)
