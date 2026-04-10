"""Report builder — assembles all analytics into a ReportDict."""

from datetime import datetime, timezone
from pathlib import Path

from src.aggregator import GradeAggregator
from src.file_io import write_report_json
from src.models import ReportDict, Student
from src.stats import semester_trends, summary_stats


def build_report(students: list[Student], semesters: list[str]) -> ReportDict:
    """Build a complete analytics report from a list of students.

    Args:
        students: List of Student objects with grades.
        semesters: Ordered list of semester labels for trend analysis.

    Returns:
        ReportDict containing all analytics results.
    """
    aggregator = GradeAggregator()
    aggregator.ingest(students)

    stats = summary_stats(students)

    report: ReportDict = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_students": len(students),
        "overall_average": float(stats["mean"]),
        "grade_distribution": dict(aggregator.grade_distribution()),
        "top_performers": aggregator.top_n(students, n=5),
        "by_major": aggregator.average_gpa_by_major(),
        "by_year": aggregator.average_gpa_by_year(),
        "semester_trends": semester_trends(students, semesters),
    }
    return report


def generate_and_save(
    students: list[Student],
    semesters: list[str],
    output_path: Path,
) -> ReportDict:
    """Build the report and persist it to a JSON file.

    Args:
        students: List of Student objects.
        semesters: Ordered semester labels.
        output_path: Path where the JSON report will be written.

    Returns:
        The generated ReportDict.
    """
    report = build_report(students, semesters)
    write_report_json(report, output_path)
    return report
