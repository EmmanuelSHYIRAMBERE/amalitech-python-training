#!/usr/bin/env python3
"""
Library Inventory Application
Main application class.
"""

from typing import Dict
from colorama import init
from src.models.library_resource import LibraryResource, Book, EBook, AudioBook, Borrower
from src.utils.file_io import save_library_data, load_library_data

# Initialize colorama
init(autoreset=True)


class LibrarySystem:
    """Main library system class."""
    
    def __init__(self):
        self.resources: Dict[str, LibraryResource] = {}
        self.borrowers: Dict[str, Borrower] = {}
        self._load_or_initialize_data()
    
    def _load_or_initialize_data(self):
        """Load data from file or initialize with sample data."""
        resources, borrowers = load_library_data()
        
        if resources and borrowers:
            self.resources = resources
            self.borrowers = borrowers
        else:
            self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample library data."""
        # Books
        book1 = Book("B001", "To Kill a Mockingbird", "Harper Lee", 1960, 
                    "978-0061120084", 324)
        book2 = Book("B002", "1984", "George Orwell", 1949,
                    "978-0451524935", 328)
        book3 = Book("B003", "Pride and Prejudice", "Jane Austen", 1813,
                    "978-0141439518", 432)
        
        # EBooks
        ebook1 = EBook("E001", "The Great Gatsby", "F. Scott Fitzgerald", 1925,
                      2.5, "PDF")
        ebook2 = EBook("E002", "Moby Dick", "Herman Melville", 1851,
                      3.2, "EPUB")
        
        # AudioBooks
        audio1 = AudioBook("A001", "Harry Potter and the Sorcerer's Stone", 
                          "J.K. Rowling", 1997, 480, "Jim Dale")
        audio2 = AudioBook("A002", "The Hobbit", "J.R.R. Tolkien", 1937,
                          660, "Andy Serkis")
        
        self.resources = {
            "B001": book1, "B002": book2, "B003": book3,
            "E001": ebook1, "E002": ebook2,
            "A001": audio1, "A002": audio2
        }
        
        # Borrowers
        borrower1 = Borrower("M001", "John Doe", "john@email.com")
        borrower2 = Borrower("M002", "Jane Smith", "jane@email.com")
        borrower3 = Borrower("M003", "Bob Johnson", "bob@email.com")
        
        self.borrowers = {
            "M001": borrower1,
            "M002": borrower2,
            "M003": borrower3
        }
        
        # Borrow some items
        book1.borrow("John Doe")
        borrower1.add_borrowed_item("B001")
        
        ebook1.borrow("Jane Smith")
        borrower2.add_borrowed_item("E001")
    
    def add_resource(self, resource: LibraryResource):
        """Add a resource to the library."""
        self.resources[resource.resource_id] = resource
        self.save_data()
    
    def remove_resource(self, resource_id: str) -> bool:
        """Remove a resource from the library."""
        if resource_id in self.resources:
            del self.resources[resource_id]
            self.save_data()
            return True
        return False
    
    def add_borrower(self, borrower: Borrower):
        """Add a borrower to the system."""
        self.borrowers[borrower.borrower_id] = borrower
        self.save_data()
    
    def remove_borrower(self, borrower_id: str) -> bool:
        """Remove a borrower from the system."""
        if borrower_id in self.borrowers:
            del self.borrowers[borrower_id]
            self.save_data()
            return True
        return False
    
    def get_all_resources(self) -> list:
        """Get all resources."""
        return list(self.resources.values())
    
    def get_all_borrowers(self) -> list:
        """Get all borrowers."""
        return list(self.borrowers.values())
    
    def save_data(self):
        """Save library data to file."""
        save_library_data(self.resources, self.borrowers)
