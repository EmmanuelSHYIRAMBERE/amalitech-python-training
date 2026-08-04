"""Tests for src/pipeline.py – functional transformations and aggregations."""

from src.pipeline import (
    by_method,
    by_status,
    by_status_range,
    client_errors,
    count_by,
    errors_only,
    server_errors,
    status_label,
    to_entries,
    top_ips,
    top_urls,
    total_bytes,
)

RAW_LINES = [
    '192.168.1.1 - - [01/Jan/2024:00:00:00 +0000] "GET / HTTP/1.1" 200 500 "-" "curl/7.68.0"',
    '192.168.1.2 - - [01/Jan/2024:00:01:00 +0000] "POST /login HTTP/1.1" 401 200 "-" "curl/7.68.0"',
    '10.0.0.1 - - [01/Jan/2024:00:02:00 +0000] "GET /api/users HTTP/1.1" 200 1500 "-" "curl/7.68.0"',
    '10.0.0.1 - - [01/Jan/2024:00:03:00 +0000] "GET /api/users HTTP/1.1" 500 0 "-" "curl/7.68.0"',
    '192.168.1.1 - - [01/Jan/2024:00:04:00 +0000] "DELETE /api/users/1 HTTP/1.1" 404 0 "-" "curl/7.68.0"',
]


def _entries():
    return list(to_entries(iter(RAW_LINES)))


class TestToEntries:
    def test_parses_all_valid_lines(self):
        assert len(_entries()) == 5

    def test_skips_invalid_lines(self):
        result = list(to_entries(iter(["garbage line", RAW_LINES[0]])))
        assert len(result) == 1


class TestFilters:
    def test_by_status(self):
        result = list(by_status(iter(_entries()), 200))
        assert len(result) == 2

    def test_by_status_range_4xx(self):
        result = list(by_status_range(iter(_entries()), 400, 499))
        assert all(400 <= e["status"] <= 499 for e in result)

    def test_by_method(self):
        result = list(by_method(iter(_entries()), "GET"))
        assert all(e["method"] == "GET" for e in result)

    def test_errors_only(self):
        result = list(errors_only(iter(_entries())))
        assert all(e["status"] >= 400 for e in result)
        assert len(result) == 3

    def test_server_errors(self):
        result = list(server_errors(iter(_entries())))
        assert all(500 <= e["status"] <= 599 for e in result)

    def test_client_errors(self):
        result = list(client_errors(iter(_entries())))
        assert all(400 <= e["status"] <= 499 for e in result)


class TestAggregations:
    def test_total_bytes(self):
        assert total_bytes(iter(_entries())) == 500 + 200 + 1500 + 0 + 0

    def test_count_by_status(self):
        counts = count_by(iter(_entries()), "status")
        assert counts[200] == 2
        assert counts[401] == 1

    def test_top_urls(self):
        urls = top_urls(iter(_entries()), n=3)
        assert urls[0][0] == "/api/users"  # most requested
        assert urls[0][1] == 2

    def test_top_ips(self):
        ips = top_ips(iter(_entries()), n=2)
        assert ips[0][0] == "10.0.0.1" or ips[0][0] == "192.168.1.1"


class TestStatusLabel:
    def test_known_codes(self):
        assert status_label(200) == "OK"
        assert status_label(404) == "Not Found"
        assert status_label(500) == "Internal Server Error"

    def test_unknown_code(self):
        assert status_label(999) == "Unknown"

    def test_cached(self):
        # calling twice should return same object (lru_cache)
        assert status_label(200) is status_label(200)
