#!/usr/bin/env python3
"""
Library Inventory Application
Library resource models with ABC and inheritance.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional


class LibraryResource(ABC):
    """Abstract base class for all library resources."""
    
    def __init__(self, resource_id: str, title: str, author: str, year: int):
        self._resource_id = resource_id
        self._title = title
        self._author = author
        self._year = year
        self._is_available = True
        self._borrowed_by: Optional[str] = None
        self._due_date: Optional[datetime] = None
    
    @property
    def resource_id(self) -> str:
        return self._resource_id
    
    @property
    def title(self) -> str:
        return self._title
    
    @property
    def author(self) -> str:
        return self._author
    
    @property
    def year(self) -> int:
        return self._year
    
    @property
    def is_available(self) -> bool:
        return self._is_available
    
    @abstractmethod
    def get_resource_type(self) -> str:
        """Return the type of resource."""
        pass
    
    @abstractmethod
    def get_loan_period(self) -> int:
        """Return loan period in days."""
        pass
    
    def borrow(self, borrower_name: str) -> bool:
        """Borrow the resource."""
        if not self._is_available:
            return False
        self._is_available = False
        self._borrowed_by = borrower_name
        self._due_date = datetime.now() + timedelta(days=self.get_loan_period())
        return True
    
    def return_resource(self) -> bool:
        """Return the resource."""
        if self._is_available:
            return False
        self._is_available = True
        self._borrowed_by = None
        self._due_date = None
        return True
    
    def is_overdue(self) -> bool:
        """Check if resource is overdue."""
        if self._is_available or not self._due_date:
            return False
        return datetime.now() > self._due_date
    
    def __repr__(self) -> str:
        return f"{self.get_resource_type()}(id='{self._resource_id}', title='{self._title}')"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, LibraryResource):
            return False
        return self._resource_id == other._resource_id
    
    def __str__(self) -> str:
        status = "Available" if self._is_available else f"Borrowed by {self._borrowed_by}"
        return f"{self._title} by {self._author} ({self._year}) - {status}"


class Book(LibraryResource):
    """Physical book resource."""
    
    def __init__(self, resource_id: str, title: str, author: str, year: int, 
                 isbn: str, pages: int):
        super().__init__(resource_id, title, author, year)
        self._isbn = isbn
        self._pages = pages
    
    @property
    def isbn(self) -> str:
        return self._isbn
    
    @property
    def pages(self) -> int:
        return self._pages
    
    def get_resource_type(self) -> str:
        return "Book"
    
    def get_loan_period(self) -> int:
        return 14  # 2 weeks


class EBook(LibraryResource):
    """Electronic book resource."""
    
    def __init__(self, resource_id: str, title: str, author: str, year: int,
                 file_size: float, format: str):
        super().__init__(resource_id, title, author, year)
        self._file_size = file_size  # in MB
        self._format = format
    
    @property
    def file_size(self) -> float:
        return self._file_size
    
    @property
    def format(self) -> str:
        return self._format
    
    def get_resource_type(self) -> str:
        return "EBook"
    
    def get_loan_period(self) -> int:
        return 21  # 3 weeks


class AudioBook(LibraryResource):
    """Audio book resource."""
    
    def __init__(self, resource_id: str, title: str, author: str, year: int,
                 duration: int, narrator: str):
        super().__init__(resource_id, title, author, year)
        self._duration = duration  # in minutes
        self._narrator = narrator
    
    @property
    def duration(self) -> int:
        return self._duration
    
    @property
    def narrator(self) -> str:
        return self._narrator
    
    def get_resource_type(self) -> str:
        return "AudioBook"
    
    def get_loan_period(self) -> int:
        return 7  # 1 week


class Author:
    """Author information."""
    
    def __init__(self, name: str, birth_year: Optional[int] = None, 
                 nationality: Optional[str] = None):
        self._name = name
        self._birth_year = birth_year
        self._nationality = nationality
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def birth_year(self) -> Optional[int]:
        return self._birth_year
    
    @property
    def nationality(self) -> Optional[str]:
        return self._nationality
    
    def __repr__(self) -> str:
        return f"Author(name='{self._name}')"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Author):
            return False
        return self._name == other._name
    
    def __str__(self) -> str:
        info = self._name
        if self._birth_year:
            info += f" (b. {self._birth_year})"
        if self._nationality:
            info += f" - {self._nationality}"
        return info


class Borrower:
    """Library borrower/member."""
    
    def __init__(self, borrower_id: str, name: str, email: str):
        self._borrower_id = borrower_id
        self._name = name
        self._email = email
        self._borrowed_items: list[str] = []
    
    @property
    def borrower_id(self) -> str:
        return self._borrower_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def email(self) -> str:
        return self._email
    
    @property
    def borrowed_items(self) -> list[str]:
        return self._borrowed_items.copy()
    
    def add_borrowed_item(self, resource_id: str):
        """Add a borrowed item."""
        if resource_id not in self._borrowed_items:
            self._borrowed_items.append(resource_id)
    
    def remove_borrowed_item(self, resource_id: str):
        """Remove a returned item."""
        if resource_id in self._borrowed_items:
            self._borrowed_items.remove(resource_id)
    
    def __repr__(self) -> str:
        return f"Borrower(id='{self._borrower_id}', name='{self._name}')"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Borrower):
            return False
        return self._borrower_id == other._borrower_id
    
    def __str__(self) -> str:
        return f"{self._name} ({self._borrower_id}) - {len(self._borrowed_items)} items borrowed"
