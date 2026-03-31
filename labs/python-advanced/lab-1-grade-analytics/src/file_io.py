"""File I/O utilities using context managers and pathlib."""

import csv
import json
import logging
from pathlib import Path
from typing import Generator

from src.models import Grade, Student

logger = logging.getLogger(__name__)


def read_students_csv(path: Path) -> list[Student]:
    """Read student records from a CSV file.

    Expected CSV columns:
        student_id, name, major, year, course_id, score, semester

    Args:
        path: Path to the CSV file.

    Returns:
        List of Student objects with grades populated.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        PermissionError: If the file cannot be read.
        ValueError: If a row contains invalid numeric data.
    """
    students: dict[str, Student] = {}
    try:
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                sid = row["student_id"].strip()
                if sid not in students:
                    students[sid] = Student(
                        student_id=sid,
                        name=row["name"].strip(),
                        major=row["major"].strip(),
                        year=int(row["year"]),
                    )
                students[sid].grades.append(
                    Grade(
                        course_id=row["course_id"].strip(),
                        score=float(row["score"]),
                        semester=row["semester"].strip(),
                    )
                )
    except FileNotFoundError:
        logger.error("CSV file not found: %s", path)
        raise
    except PermissionError:
        logger.error("Permission denied reading: %s", path)
        raise
    except (ValueError, KeyError) as exc:
        logger.error("Invalid data in CSV: %s", exc)
        raise ValueError(f"Malformed CSV row: {exc}") from exc

    logger.info("Loaded %d students from %s", len(students), path)
    return list(students.values())


def stream_students_csv(path: Path) -> Generator[Student, None, None]:
    """Generator version of read_students_csv for memory-efficient processing.

    Yields one fully-built Student per unique student_id encountered.
    Note: buffers rows per student_id internally, then yields on flush.

    Args:
        path: Path to the CSV file.

    Yields:
        Student objects one at a time.
    """
    buffer: dict[str, Student] = {}
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            sid = row["student_id"].strip()
            if sid not in buffer:
                buffer[sid] = Student(
                    student_id=sid,
                    name=row["name"].strip(),
                    major=row["major"].strip(),
                    year=int(row["year"]),
                )
            buffer[sid].grades.append(
                Grade(
                    course_id=row["course_id"].strip(),
                    score=float(row["score"]),
                    semester=row["semester"].strip(),
                )
            )
    yield from buffer.values()


def write_report_json(report: dict, path: Path) -> None:
    """Write a report dictionary to a JSON file.

    Args:
        report: Report data to serialise.
        path: Destination file path.

    Raises:
        PermissionError: If the file cannot be written.
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2)
        logger.info("Report written to %s", path)
    except PermissionError:
        logger.error("Permission denied writing report: %s", path)
        raise
