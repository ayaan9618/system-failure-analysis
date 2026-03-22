import argparse
import sys
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


APP_NAME = "LogLens"
DEFAULT_OUTPUT_DIR = "output"
APP_VERSION = "v1.0"
ASCII_BANNER = r"""
 _                 _                      
| |    ___   __ _ | |    ___  _ __   ___  
| |   / _ \ / _` || |   / _ \| '_ \ / __| 
| |__| (_) | (_| || |__|  __/| | | |\__ \ 
|_____\___/ \__, ||_____\___||_| |_||___/ 
            |___/                         
"""


def run_analysis(
    log_path,
    output_dir=DEFAULT_OUTPUT_DIR,
    generate_charts=True,
    generate_pdf=True,
):
    output_dir = Path(output_dir)
    reports_dir = output_dir / "reports"
    charts_dir = output_dir / "charts"
    text_report_path = reports_dir / "system_failure_report.txt"
    pdf_report_path = reports_dir / "system_failure_report.pdf"

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

    if generate_charts:
        chart_paths = {
            "error_frequency": plot_error_frequency(error_analysis, charts_dir),
            "log_levels": plot_log_levels(logs, charts_dir),
            "error_timeline": plot_error_timeline(incident_details, charts_dir),
        }
    else:
        chart_paths = {
            "error_frequency": None,
            "log_levels": None,
            "error_timeline": None,
        }

    text_report, text_report_path = generate_report(
        incident_details,
        downtime,
        error_analysis,
        root_cause,
        text_report_path,
    )

    pdf_path = None
    if generate_pdf:
        pdf_path = generate_pdf_report(
            incident_details,
            downtime,
            error_analysis,
            root_cause,
            pdf_report_path,
        )

    return {
        "log_path": str(log_path),
        "logs": logs,
        "incident_details": incident_details,
        "downtime": downtime,
        "error_analysis": error_analysis,
        "root_cause": root_cause,
        "text_report": text_report,
        "text_report_path": text_report_path,
        "chart_paths": chart_paths,
        "pdf_path": pdf_path,
        "generate_charts": generate_charts,
        "generate_pdf": generate_pdf,
    }


def prompt_for_log_path():
    print("Enter the log file path to analyze.")
    while True:
        user_input = input("Log file path: ").strip()
        selected_path = user_input

        if not selected_path:
            print("Log file path is required.")
            continue
        if Path(selected_path).exists():
            return selected_path

        print(f"File not found: {selected_path}")
        print("Please enter a valid log file path.")


def prompt_for_output_dir(default_output_dir=DEFAULT_OUTPUT_DIR):
    print(f"Press Enter to use the default output directory: {default_output_dir}")
    user_input = input("Output directory: ").strip()
    return user_input or default_output_dir


def prompt_yes_no(prompt_text, default=True):
    default_hint = "Y/n" if default else "y/N"

    while True:
        user_input = input(f"{prompt_text} [{default_hint}]: ").strip().lower()
        if not user_input:
            return default
        if user_input in {"y", "yes"}:
            return True
        if user_input in {"n", "no"}:
            return False
        print("Please enter yes or no.")


def run_interactive_menu():
    _print_home_screen()
    _print_command_list()

    while True:
        choice = input("\nloglens> ").strip().lower()

        if choice in {"1", "/analyze", "analyze"}:
            log_path = prompt_for_log_path()
            output_dir = prompt_for_output_dir()
            generate_charts = prompt_yes_no("Generate charts?", default=True)
            generate_pdf = prompt_yes_no("Generate PDF report?", default=True)

            result = run_analysis(
                log_path=log_path,
                output_dir=output_dir,
                generate_charts=generate_charts,
                generate_pdf=generate_pdf,
            )
            print_summary(result)
            if prompt_yes_no("\nRun another command?", default=True):
                continue
            return 0

        if choice in {"2", "/analyzeq", "analyzeq", "/quick", "quick"}:
            log_path = prompt_for_log_path()
            result = run_analysis(
                log_path=log_path,
                output_dir=DEFAULT_OUTPUT_DIR,
                generate_charts=True,
                generate_pdf=True,
            )
            print_summary(result)
            if prompt_yes_no("\nRun another command?", default=True):
                continue
            return 0

        if choice in {"3", "/examples", "examples"}:
            print("\nCLI usage examples:")
            print("python main.py")
            print("python main.py logs\\cloud_failure_log.json -o my_output")
            print("python main.py --input logs\\reader.deployment.log --skip-pdf")
            continue

        if choice in {"/help", "help", "-h", "--help"}:
            _print_help_screen()
            continue

        if choice in {"4", "/about", "about"}:
            print(f"\n{APP_NAME} {APP_VERSION}")
            print("Intelligent log analysis and failure diagnosis for cloud incidents.")
            print(f"Default output: {DEFAULT_OUTPUT_DIR}")
            continue

        if choice in {"5", "/exit", "exit", "quit"}:
            print("Exiting LogLens.")
            return 0

        print("Unknown command. Try /analyze, /quick, /examples, /about, or /exit.")


def _print_home_screen():
    print(ASCII_BANNER)
    print(f"{APP_NAME} {APP_VERSION}")
    print("Intelligent log analysis and failure diagnosis for cloud incidents.\n")
    print("Default output:", DEFAULT_OUTPUT_DIR)
    print("\nTips:")
    print("  /analyze   guided analysis")
    print("  /analyzeq  ask only for log path, then run with default output settings")
    print("  /help      show command help")
    print("  /examples  show CLI examples")
    print("  /exit      quit the app")


def _print_command_list():
    print("\nAvailable commands:")
    print("  /analyze   analyze a log file with guided setup")
    print("  /analyzeq  analyze a log file with quick default output settings")
    print("  /examples  show command-line usage examples")
    print("  /help      show command help")
    print("  /about     show app info")
    print("  /exit      close LogLens")


def _print_help_screen():
    print(f"\n{APP_NAME} commands:")
    print("  /analyze   ask for log path, output directory, chart choice, and PDF choice")
    print("  /analyzeq  ask for log path only and run with default output settings")
    print("  /examples  show command-line usage examples")
    print("  /about     redraw the home screen")
    print("  /help      show this help")
    print("  /exit      close the app")
    print("\nCommand-line flags:")
    print("  -h, --help         show argparse help")
    print("  -i, --input        path to log file")
    print("  -o, --output-dir   output directory")
    print("  --skip-charts      disable chart generation")
    print("  --skip-pdf         disable PDF generation")
    print("  --no-prompt        require CLI input or fail without opening the menu")


def print_summary(result):
    incident_details = result["incident_details"]
    downtime = result["downtime"]
    error_analysis = result["error_analysis"]
    root_cause = result["root_cause"]

    print(f"{APP_NAME} analysis completed successfully.")
    print(f"Input File: {result['log_path']}")

    print(ASCII_BANNER)
    print(f"{APP_NAME} {APP_VERSION}")
    print("Intelligent log analysis and failure diagnosis for cloud incidents.\n")
    
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
    print(f"Text report saved to: {result['text_report_path']}")

    if result["generate_pdf"]:
        if result["pdf_path"]:
            print(f"PDF report saved to: {result['pdf_path']}")
        else:
            print("PDF report skipped: reportlab is not installed")
    else:
        print("PDF report skipped: disabled by CLI option")

    if result["generate_charts"]:
        for chart_name, chart_path in result["chart_paths"].items():
            if chart_path:
                print(f"{chart_name} chart saved to: {chart_path}")
            else:
                print(f"{chart_name} chart skipped: matplotlib is not installed")
    else:
        print("Charts skipped: disabled by CLI option")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="loglens",
        description="LogLens: analyze infrastructure and application logs for failure diagnosis.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Path to the log file to analyze.",
    )
    parser.add_argument(
        "-i",
        "--input",
        dest="input_option",
        help="Path to the log file to analyze.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where reports and charts will be written.",
    )
    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="Do not open the interactive menu when no input path is provided.",
    )
    parser.add_argument(
        "--skip-charts",
        action="store_true",
        help="Skip chart generation.",
    )
    parser.add_argument(
        "--skip-pdf",
        action="store_true",
        help="Skip PDF report generation.",
    )
    return parser


def resolve_log_path(args):
    selected_path = args.input_option or args.input

    if selected_path:
        return selected_path

    if args.no_prompt:
        raise ValueError("A log file path is required when using --no-prompt.")

    return prompt_for_log_path()


def main():
    parser = build_parser()
    try:
        args = parser.parse_args()
    except SystemExit as exc:
        return exc.code

    if len(sys.argv) == 1:
        return run_interactive_menu()

    try:
        log_path = resolve_log_path(args)
    except ValueError as error:
        parser.error(str(error))
        return 2
    analysis_result = run_analysis(
        log_path=log_path,
        output_dir=args.output_dir,
        generate_charts=not args.skip_charts,
        generate_pdf=not args.skip_pdf,
    )
    print_summary(analysis_result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
