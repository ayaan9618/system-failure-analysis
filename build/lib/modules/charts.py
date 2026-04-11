from pathlib import Path

try:
    import matplotlib

    matplotlib.use("Agg")

    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    matplotlib = None
    plt = None


DEFAULT_CHARTS_DIR = Path("output/charts")


def plot_error_frequency(error_analysis, output_dir=DEFAULT_CHARTS_DIR):
    """
    Plot the most frequent error patterns.
    """

    charts_dir = Path(output_dir)
    chart_path = charts_dir / "error_frequency_chart.png"
    charts_dir.mkdir(parents=True, exist_ok=True)
    if plt is None:
        return None

    top_errors = error_analysis.get("top_errors", [])[:8]
    if not top_errors:
        return None

    labels = [_truncate(label) for label, _ in top_errors]
    counts = [count for _, count in top_errors]

    figure, axis = plt.subplots(figsize=(10, 5))
    axis.bar(labels, counts, color="#d95f02")
    axis.set_title("Top Error Messages")
    axis.set_xlabel("Error")
    axis.set_ylabel("Occurrences")
    axis.tick_params(axis="x", rotation=35)

    figure.tight_layout()
    figure.savefig(chart_path)
    plt.close(figure)

    return chart_path


def plot_log_levels(logs, output_dir=DEFAULT_CHARTS_DIR):
    """
    Plot distribution of log levels across the loaded dataset.
    """

    charts_dir = Path(output_dir)
    chart_path = charts_dir / "log_level_distribution.png"
    charts_dir.mkdir(parents=True, exist_ok=True)
    if plt is None:
        return None

    level_counts = {}
    for log in logs:
        level = log["level"]
        level_counts[level] = level_counts.get(level, 0) + 1

    if not level_counts:
        return None

    labels = list(level_counts.keys())
    values = list(level_counts.values())

    figure, axis = plt.subplots(figsize=(7, 7))
    axis.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    axis.set_title("Log Level Distribution")

    figure.tight_layout()
    figure.savefig(chart_path)
    plt.close(figure)

    return chart_path


def plot_error_timeline(incident_details, output_dir=DEFAULT_CHARTS_DIR):
    """
    Plot error events across the incident timeline.
    """

    charts_dir = Path(output_dir)
    chart_path = charts_dir / "error_timeline.png"
    charts_dir.mkdir(parents=True, exist_ok=True)
    if plt is None:
        return None

    timeline = incident_details.get("timeline", [])
    error_events = [log for log in timeline if log["level"] == "ERROR"]
    if not error_events:
        return None

    x_values = [log["timestamp"] for log in error_events]
    y_values = list(range(1, len(error_events) + 1))

    figure, axis = plt.subplots(figsize=(10, 4))
    axis.plot(x_values, y_values, marker="o", linestyle="-", color="#7570b3")
    axis.set_title("Incident Error Timeline")
    axis.set_xlabel("Time")
    axis.set_ylabel("Error Sequence")
    axis.tick_params(axis="x", rotation=35)

    figure.tight_layout()
    figure.savefig(chart_path)
    plt.close(figure)

    return chart_path


def _truncate(label, limit=45):
    if len(label) <= limit:
        return label
    return label[: limit - 3] + "..."
