"""Tests for src/generators.py – generator and itertools utilities."""

from pathlib import Path

import pytest

from src.generators import batch, group_by, takewhile_date


def _make_entries():
    import datetime
    return [
        {"ip": "1.1.1.1", "status": 200, "hour": 0, "timestamp": datetime.datetime(2024, 1, 1, 0, 0)},
        {"ip": "1.1.1.2", "status": 404, "hour": 1, "timestamp": datetime.datetime(2024, 1, 1, 1, 0)},
        {"ip": "1.1.1.1", "status": 200, "hour": 2, "timestamp": datetime.datetime(2024, 1, 2, 2, 0)},
        {"ip": "1.1.1.3", "status": 500, "hour": 3, "timestamp": datetime.datetime(2024, 1, 3, 3, 0)},
    ]


class TestBatch:
    def test_splits_correctly(self):
        chunks = list(batch(iter(_make_entries()), 2))
        assert len(chunks) == 2
        assert len(chunks[0]) == 2

    def test_last_chunk_smaller(self):
        chunks = list(batch(iter(_make_entries()), 3))
        assert len(chunks[-1]) == 1

    def test_empty_input(self):
        assert list(batch(iter([]), 10)) == []


class TestGroupBy:
    def test_groups_by_status(self):
        groups = dict(
            (k, list(v)) for k, v in group_by(_make_entries(), "status")
        )
        assert 200 in groups
        assert len(groups[200]) == 2

    def test_groups_by_hour(self):
        groups = dict(
            (k, list(v)) for k, v in group_by(_make_entries(), "hour")
        )
        assert len(groups) == 4


class TestTakewhileDate:
    def test_filters_date_range(self):
        result = list(takewhile_date(_make_entries(), "2024-01-01", "2024-01-02"))
        assert all(e["timestamp"].strftime("%Y-%m-%d") <= "2024-01-02" for e in result)
        assert len(result) == 3

    def test_empty_when_out_of_range(self):
        result = list(takewhile_date(_make_entries(), "2025-01-01", "2025-12-31"))
        assert result == []


class TestReadLogLines:
    def test_reads_file_line_by_line(self, tmp_path):
        from src.generators import read_log_lines
        log = tmp_path / "test.log"
        log.write_text("line1\nline2\nline3\n", encoding="utf-8")
        lines = list(read_log_lines(log))
        assert len(lines) == 3
        assert lines[0].strip() == "line1"
