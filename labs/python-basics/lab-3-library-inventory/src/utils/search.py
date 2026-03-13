#!/usr/bin/env python3
"""
Search and filter utilities using list comprehensions.
"""

from typing import List
from src.models.library_resource import LibraryResource


def search_by_title(resources: List[LibraryResource], query: str) -> List[LibraryResource]:
    """Search resources by title using list comprehension."""
    return [r for r in resources if query.lower() in r.title.lower()]


def search_by_author(resources: List[LibraryResource], query: str) -> List[LibraryResource]:
    """Search resources by author using list comprehension."""
    return [r for r in resources if query.lower() in r.author.lower()]


def filter_by_type(resources: List[LibraryResource], resource_type: str) -> List[LibraryResource]:
    """Filter resources by type using list comprehension."""
    return [r for r in resources if r.get_resource_type() == resource_type]


def filter_available(resources: List[LibraryResource]) -> List[LibraryResource]:
    """Get all available resources using list comprehension."""
    return [r for r in resources if r.is_available]


def filter_borrowed(resources: List[LibraryResource]) -> List[LibraryResource]:
    """Get all borrowed resources using list comprehension."""
    return [r for r in resources if not r.is_available]


def filter_overdue(resources: List[LibraryResource]) -> List[LibraryResource]:
    """Get all overdue resources using list comprehension."""
    return [r for r in resources if r.is_overdue()]


def filter_by_year_range(resources: List[LibraryResource], 
                         start_year: int, end_year: int) -> List[LibraryResource]:
    """Filter resources by year range using list comprehension."""
    return [r for r in resources if start_year <= r.year <= end_year]


def get_unique_authors(resources: List[LibraryResource]) -> List[str]:
    """Get unique authors using set comprehension."""
    return sorted(list({r.author for r in resources}))


def get_resources_by_author(resources: List[LibraryResource], 
                            author: str) -> List[LibraryResource]:
    """Get all resources by specific author using list comprehension."""
    return [r for r in resources if r.author.lower() == author.lower()]


def categorize_by_type(resources: List[LibraryResource]) -> dict:
    """Categorize resources by type using dict comprehension."""
    types = {r.get_resource_type() for r in resources}
    return {t: [r for r in resources if r.get_resource_type() == t] for t in types}


def get_statistics(resources: List[LibraryResource]) -> dict:
    """Generate statistics using comprehensions."""
    return {
        'total': len(resources),
        'available': len([r for r in resources if r.is_available]),
        'borrowed': len([r for r in resources if not r.is_available]),
        'overdue': len([r for r in resources if r.is_overdue()]),
        'by_type': {t: len(items) for t, items in categorize_by_type(resources).items()}
    }
