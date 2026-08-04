# Lab 1 — Student Grade Analytics Tool

A Python 3.11+ analytics tool that processes student records from CSV files,
calculates statistics, and generates JSON reports using advanced collections.

---

## Setup

```bash
git clone https://github.com/EmmanuelSHYIRAMBERE/amalitech-python-training.git
cd labs/python-advanced/lab-1-grade-analytics
pip install -r requirements.txt
```

---

## Run

```bash
python main.py
```

---

## Run Tests

```bash
pytest
```

---

## Project Structure

```
lab-1-grade-analytics/
├── src/
│   ├── models.py       ← dataclasses: Student, Course, Grade + TypedDict
│   ├── aggregator.py   ← Counter, defaultdict, OrderedDict, deque
│   ├── stats.py        ← mean, median, mode, percentile, trends
│   ├── file_io.py      ← CSV reader, JSON writer, pathlib, generators
│   └── reporter.py     ← assembles ReportDict and writes JSON
├── tests/
│   ├── test_models.py
│   ├── test_aggregator.py
│   ├── test_stats.py
│   └── test_file_io.py
├── sample_data/
│   └── students.csv
├── reports/            ← generated JSON reports (git-ignored)
├── main.py
├── requirements.txt
└── pyproject.toml
```

---

## Sample Input (students.csv)

```
student_id,name,major,year,course_id,score,semester
S001,Alice Mugisha,Computer Science,2,CS101,92,2024-S1
S001,Alice Mugisha,Computer Science,2,CS102,88,2024-S1
S002,Bob Nkurunziza,Mathematics,3,MA101,75,2024-S1
```

---

## Sample Output (terminal)

```
========== GRADE ANALYTICS REPORT ==========
Generated at  : 2024-11-01T10:00:00+00:00
Total students: 10
Overall avg   : 81.04

Grade Distribution:
  A: 8
  B: 9
  C: 5
  D: 2
  F: 1

Top Performers:
  1. Grace Mukamana — GPA: 97.67
  2. David Habimana — GPA: 91.33
  3. Alice Mugisha  — GPA: 91.67
```

---

## Sample JSON Report

```json
{
  "generated_at": "2024-11-01T10:00:00+00:00",
  "total_students": 10,
  "overall_average": 81.04,
  "grade_distribution": { "A": 8, "B": 9, "C": 5, "D": 2, "F": 1 },
  "top_performers": [
    { "student_id": "S007", "name": "Grace Mukamana", "gpa": 97.67 }
  ],
  "by_major": { "Computer Science": 91.2, "Mathematics": 73.5 },
  "by_year": { "1": 80.0, "2": 79.5, "3": 74.0, "4": 90.5 },
  "semester_trends": { "2024-S1": 80.1, "2024-S2": 83.6 }
}
```

---

## Collection Performance Notes

| Collection    | Used for                        | Why                                              |
|---------------|---------------------------------|--------------------------------------------------|
| Counter       | Letter grade frequency          | O(1) increment, built-in most_common()           |
| defaultdict   | Group GPAs by major / year      | Eliminates key-existence checks                  |
| OrderedDict   | Grade distribution A→F          | Guarantees insertion order in report output      |
| deque(maxlen) | Rolling average of last N GPAs  | O(1) append/pop, fixed memory regardless of size |
| Generator     | stream_students_csv()           | Processes large CSVs without loading all in RAM  |

Memory trade-off: a plain `list` of all rows uses O(n) memory upfront.
The generator approach in `stream_students_csv` keeps only one row in memory
at a time, making it suitable for files with millions of records.
