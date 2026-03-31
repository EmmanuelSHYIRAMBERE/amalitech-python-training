"""CLI entry point for the Student Grade Analytics Tool."""

import logging
from pathlib import Path

from src.file_io import read_students_csv
from src.reporter import generate_and_save

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

SEMESTERS = ["2024-S1", "2024-S2"]
CSV_PATH = Path("sample_data/students.csv")
REPORT_PATH = Path("reports/report.json")


def main() -> None:
    """Run the grade analytics pipeline."""
    logger.info("Starting Student Grade Analytics Tool")

    students = read_students_csv(CSV_PATH)
    report = generate_and_save(students, SEMESTERS, REPORT_PATH)

    print("\n========== GRADE ANALYTICS REPORT ==========")
    print(f"Generated at  : {report['generated_at']}")
    print(f"Total students: {report['total_students']}")
    print(f"Overall avg   : {report['overall_average']}")

    print("\nGrade Distribution:")
    for letter, count in report["grade_distribution"].items():
        print(f"  {letter}: {count}")

    print("\nTop Performers:")
    for i, s in enumerate(report["top_performers"], 1):
        print(f"  {i}. {s['name']} — GPA: {s['gpa']}")

    print("\nAverage GPA by Major:")
    for major, avg in report["by_major"].items():
        print(f"  {major}: {avg}")

    print("\nAverage GPA by Year:")
    for year, avg in sorted(report["by_year"].items()):
        print(f"  Year {year}: {avg}")

    print("\nSemester Trends:")
    for semester, avg in report["semester_trends"].items():
        print(f"  {semester}: {avg}")

    print(f"\nFull report saved to: {REPORT_PATH}")
    print("=============================================\n")


if __name__ == "__main__":
    main()
