"""Pytest suite for divide_funds — 100% coverage."""

import pytest

from calculator import divide_funds


def test_valid_division():
    assert divide_funds(100, 4) == 25.0


def test_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide_funds(100, 0)


def test_invalid_type_string():
    with pytest.raises(TypeError):
        divide_funds("100", 4)
