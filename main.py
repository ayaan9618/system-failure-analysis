from modules.log_input import load_logs
from modules.log_parser import parse_logs
from modules.failure_detection import detect_failure, detect_failure_details
from modules.downtime_calculator import calculate_downtime
from modules.error_analysis import analyze_errors
from modules.root_cause_analysis import detect_root_cause
from modules.report_generator import generate_report
from modules.charts import plot_error_frequency, plot_log_levels, plot_error_timeline
from modules.pdf_report_generator import generate_pdf_report


# Load and parse logs
raw_logs = load_logs("logs/cloud_failure_log.json")
logs = parse_logs(raw_logs)
print("Logs loaded and parsed successfully!\n")

for log in logs:
    print(log)


# Failure Detection
print("\n------ Failure Analysis ------")

incident_details = detect_failure_details(logs)
failure_start, failure_end = detect_failure(logs)

print("Failure Start Time:", failure_start)
print("Failure End Time:", failure_end)
print("Incident Status:", incident_details["status"])


# Downtime Calculation
print("\n------ Downtime Report ------")

downtime = calculate_downtime(failure_start, failure_end)

print("Total Downtime:", downtime)


# Error Pattern Analysis
print("\n------ Error Pattern Analysis ------")

error_analysis = analyze_errors(incident_details["timeline"] or logs)
total_errors = error_analysis["total_errors"]
error_counts = error_analysis["error_counts"]

print("Total Errors:", total_errors)

print("\nError Frequency:")
for error, count in error_counts.items():
    print(f"{error} → {count}")


# Root Cause Detection
print("\n------ Root Cause Detection ------")

root_cause = detect_root_cause(error_analysis)

print("Predicted Root Cause:", root_cause["summary"])


# Generate Report
print("\n------ Report Generated ------")

generate_report(
    incident_details,
    downtime,
    error_analysis,
    root_cause
)

print("Report saved to: output/reports/system_failure_report.txt")


# Generate Charts
plot_error_frequency(error_counts)
plot_log_levels(logs)
plot_error_timeline(logs)

generate_pdf_report(
    incident_details,
    downtime,
    error_analysis,
    root_cause
)
