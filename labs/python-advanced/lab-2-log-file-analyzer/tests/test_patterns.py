"""Tests for src/patterns.py – regex pattern correctness."""

import pytest

from src.patterns import (
    EMAIL_VALIDATE,
    IP_VALIDATE,
    LOG_LINE,
    QUERY_STRIP,
    TIMESTAMP,
    URL_VALIDATE,
)

SAMPLE_LINE = (
    '192.168.1.1 - - [01/Jan/2024:00:00:00 +0000] '
    '"GET /api/users HTTP/1.1" 200 1234 "-" "curl/7.68.0"'
)


class TestLogLinePattern:
    def test_matches_valid_line(self):
        assert LOG_LINE.match(SAMPLE_LINE) is not None

    def test_named_groups(self):
        m = LOG_LINE.match(SAMPLE_LINE)
        assert m["ip"] == "192.168.1.1"
        assert m["method"] == "GET"
        assert m["url"] == "/api/users"
        assert m["status"] == "200"
        assert m["size"] == "1234"
        assert m["agent"] == "curl/7.68.0"

    def test_no_match_on_garbage(self):
        assert LOG_LINE.match("not a log line") is None

    def test_post_method(self):
        line = (
            '10.0.0.1 - - [15/Mar/2024:12:30:00 +0000] '
            '"POST /login HTTP/1.1" 401 0 "-" "python-requests/2.28.0"'
        )
        m = LOG_LINE.match(line)
        assert m is not None
        assert m["method"] == "POST"
        assert m["status"] == "401"

    def test_size_zero(self):
        line = (
            '10.0.0.2 - - [01/Jan/2024:01:00:00 +0000] '
            '"DELETE /api/users/1 HTTP/1.1" 204 0 "-" "curl/7.68.0"'
        )
        m = LOG_LINE.match(line)
        assert m["size"] == "0"


class TestTimestampPattern:
    def test_extracts_components(self):
        m = TIMESTAMP.match("01/Jan/2024:08:30:45 +0000")
        assert m["day"] == "01"
        assert m["month"] == "Jan"
        assert m["year"] == "2024"
        assert m["hour"] == "08"
        assert m["minute"] == "30"
        assert m["second"] == "45"

    def test_no_match_on_invalid(self):
        assert TIMESTAMP.match("2024-01-01 08:30:45") is None


class TestValidationPatterns:
    @pytest.mark.parametrize("ip", ["192.168.1.1", "10.0.0.1", "255.255.255.0"])
    def test_valid_ips(self, ip):
        assert IP_VALIDATE.match(ip) is not None

    @pytest.mark.parametrize("ip", ["999.0.0.1", "192.168.1", "abc.def.ghi.jkl"])
    def test_invalid_ips(self, ip):
        assert IP_VALIDATE.match(ip) is None

    @pytest.mark.parametrize("email", ["user@example.com", "a.b+c@domain.org"])
    def test_valid_emails(self, email):
        assert EMAIL_VALIDATE.match(email) is not None

    @pytest.mark.parametrize("email", ["notanemail", "@domain.com", "user@"])
    def test_invalid_emails(self, email):
        assert EMAIL_VALIDATE.match(email) is None

    @pytest.mark.parametrize("url", ["https://example.com", "http://foo.bar/path"])
    def test_valid_urls(self, url):
        assert URL_VALIDATE.match(url) is not None

    @pytest.mark.parametrize("url", ["ftp://example.com", "not-a-url"])
    def test_invalid_urls(self, url):
        assert URL_VALIDATE.match(url) is None


class TestCleaningPatterns:
    def test_query_strip(self):
        assert QUERY_STRIP.sub("", "/api/search?q=python") == "/api/search"

    def test_query_strip_no_query(self):
        assert QUERY_STRIP.sub("", "/api/users") == "/api/users"
