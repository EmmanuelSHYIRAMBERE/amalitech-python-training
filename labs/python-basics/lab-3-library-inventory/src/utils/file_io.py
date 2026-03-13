#!/usr/bin/env python3
"""
File I/O utilities for library data persistence.
"""

import json
import os
from typing import Dict, List
from src.models.library_resource import LibraryResource, Book, EBook, AudioBook, Borrower


def save_library_data(resources: Dict[str, LibraryResource], 
                      borrowers: Dict[str, Borrower],
                      filename: str = "src/data/library_data.json"):
    """
    Save library data to JSON file.
    
    Args:
        resources: Dictionary of library resources
        borrowers: Dictionary of borrowers
        filename: Path to save file
    """
    data = {
        'resources': [],
        'borrowers': []
    }
    
    # Serialize resources
    for resource in resources.values():
        resource_data = {
            'resource_id': resource.resource_id,
            'title': resource.title,
            'author': resource.author,
            'year': resource.year,
            'type': resource.get_resource_type(),
            'is_available': resource.is_available,
            'borrowed_by': resource._borrowed_by,
            'due_date': resource._due_date.isoformat() if resource._due_date else None
        }
        
        if isinstance(resource, Book):
            resource_data['isbn'] = resource.isbn
            resource_data['pages'] = resource.pages
        elif isinstance(resource, EBook):
            resource_data['file_size'] = resource.file_size
            resource_data['format'] = resource.format
        elif isinstance(resource, AudioBook):
            resource_data['duration'] = resource.duration
            resource_data['narrator'] = resource.narrator
        
        data['resources'].append(resource_data)
    
    # Serialize borrowers
    for borrower in borrowers.values():
        borrower_data = {
            'borrower_id': borrower.borrower_id,
            'name': borrower.name,
            'email': borrower.email,
            'borrowed_items': borrower.borrowed_items
        }
        data['borrowers'].append(borrower_data)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Write to file
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)


def load_library_data(filename: str = "src/data/library_data.json") -> tuple:
    """
    Load library data from JSON file.
    
    Args:
        filename: Path to load file
        
    Returns:
        Tuple of (resources dict, borrowers dict)
    """
    if not os.path.exists(filename):
        return {}, {}
    
    with open(filename, 'r') as f:
        data = json.load(f)
    
    resources = {}
    borrowers = {}
    
    # Deserialize resources
    for res_data in data.get('resources', []):
        resource_type = res_data['type']
        
        if resource_type == 'Book':
            resource = Book(
                res_data['resource_id'],
                res_data['title'],
                res_data['author'],
                res_data['year'],
                res_data['isbn'],
                res_data['pages']
            )
        elif resource_type == 'EBook':
            resource = EBook(
                res_data['resource_id'],
                res_data['title'],
                res_data['author'],
                res_data['year'],
                res_data['file_size'],
                res_data['format']
            )
        elif resource_type == 'AudioBook':
            resource = AudioBook(
                res_data['resource_id'],
                res_data['title'],
                res_data['author'],
                res_data['year'],
                res_data['duration'],
                res_data['narrator']
            )
        else:
            continue
        
        # Restore borrowed state
        if not res_data['is_available']:
            resource._is_available = False
            resource._borrowed_by = res_data['borrowed_by']
            if res_data['due_date']:
                from datetime import datetime
                resource._due_date = datetime.fromisoformat(res_data['due_date'])
        
        resources[resource.resource_id] = resource
    
    # Deserialize borrowers
    for bor_data in data.get('borrowers', []):
        borrower = Borrower(
            bor_data['borrower_id'],
            bor_data['name'],
            bor_data['email']
        )
        borrower._borrowed_items = bor_data['borrowed_items']
        borrowers[borrower.borrower_id] = borrower
    
    return resources, borrowers


def export_to_text(resources: List[LibraryResource], filename: str):
    """
    Export library resources to text file.
    
    Args:
        resources: List of library resources
        filename: Path to save file
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w') as f:
        f.write("LIBRARY INVENTORY REPORT\n")
        f.write("=" * 60 + "\n\n")
        
        for resource in resources:
            f.write(f"ID: {resource.resource_id}\n")
            f.write(f"Title: {resource.title}\n")
            f.write(f"Author: {resource.author}\n")
            f.write(f"Year: {resource.year}\n")
            f.write(f"Type: {resource.get_resource_type()}\n")
            f.write(f"Status: {'Available' if resource.is_available else 'Borrowed'}\n")
            f.write("-" * 60 + "\n")
