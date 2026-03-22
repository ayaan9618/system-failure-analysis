from pathlib import Path

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet


def generate_pdf_report(incident_details, downtime, error_analysis, root_cause):
    """
    Generate a PDF incident report with analysis and charts.
    """

    pdf_path = Path("output/reports/system_failure_report.pdf")
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("AI-Based System Failure Analysis Report", styles["Title"]))
    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            f"Incident Status: {incident_details.get('status', 'unknown')}",
            styles["Normal"],
        )
    )
    elements.append(
        Paragraph(
            f"Failure Start Time: {incident_details.get('failure_start')}",
            styles["Normal"],
        )
    )
    elements.append(
        Paragraph(
            f"Failure End Time: {incident_details.get('failure_end')}",
            styles["Normal"],
        )
    )
    elements.append(Paragraph(f"Total Downtime: {downtime}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(f"Total Errors: {error_analysis.get('total_errors', 0)}", styles["Normal"])
    )
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Top Error Messages", styles["Heading2"]))
    for error, count in error_analysis.get("top_errors", []):
        elements.append(Paragraph(f"{error} : {count}", styles["Normal"]))

    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Affected Modules", styles["Heading2"]))
    for module, count in error_analysis.get("top_affected_modules", []):
        elements.append(Paragraph(f"{module} : {count}", styles["Normal"]))

    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Predicted Root Cause", styles["Heading2"]))
    elements.append(
        Paragraph(f"Summary: {root_cause.get('summary', 'Unknown')}", styles["Normal"])
    )
    elements.append(
        Paragraph(f"Category: {root_cause.get('category', 'unknown')}", styles["Normal"])
    )
    elements.append(
        Paragraph(f"Confidence: {root_cause.get('confidence', 'low')}", styles["Normal"])
    )
    for evidence_item in root_cause.get("evidence", []):
        elements.append(Paragraph(f"Evidence: {evidence_item}", styles["Normal"]))

    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Incident Timeline Summary", styles["Heading2"]))
    for item in incident_details.get("timeline_summary", [])[:12]:
        elements.append(
            Paragraph(
                f"{item['timestamp']} | {item['level']} | {item['message']}",
                styles["Normal"],
            )
        )

    chart_paths = [
        Path("output/charts/error_frequency_chart.png"),
        Path("output/charts/log_level_distribution.png"),
        Path("output/charts/error_timeline.png"),
    ]

    existing_charts = [path for path in chart_paths if path.exists()]
    if existing_charts:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Charts", styles["Heading2"]))
        elements.append(Spacer(1, 10))
        for chart_path in existing_charts:
            elements.append(Image(str(chart_path), width=400, height=250))
            elements.append(Spacer(1, 20))

    pdf = SimpleDocTemplate(str(pdf_path))
    pdf.build(elements)
