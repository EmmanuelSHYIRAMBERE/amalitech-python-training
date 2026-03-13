#!/usr/bin/env python3
"""
Report generation for library inventory.
"""

from datetime import datetime
from typing import List
from tabulate import tabulate
from src.models.library_resource import LibraryResource, Borrower
from src.utils.search import get_statistics, categorize_by_type


def generate_inventory_report(resources: List[LibraryResource]) -> str:
    """Generate inventory report."""
    output = "\n" + "="*60 + "\n"
    output += "LIBRARY INVENTORY REPORT".center(60) + "\n"
    output += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(60) + "\n"
    output += "="*60 + "\n\n"
    
    if not resources:
        return output + "No resources in library.\n"
    
    data = []
    for r in resources:
        data.append([
            r.resource_id,
            r.title[:30],
            r.author[:20],
            r.year,
            r.get_resource_type(),
            "Yes" if r.is_available else "No"
        ])
    
    table = tabulate(data, 
                    headers=['ID', 'Title', 'Author', 'Year', 'Type', 'Available'],
                    tablefmt='grid')
    
    stats = get_statistics(resources)
    summary = f"\n\nSummary:\n"
    summary += f"  Total Resources: {stats['total']}\n"
    summary += f"  Available: {stats['available']}\n"
    summary += f"  Borrowed: {stats['borrowed']}\n"
    summary += f"  Overdue: {stats['overdue']}\n"
    
    return output + table + summary


def generate_borrowed_report(resources: List[LibraryResource]) -> str:
    """Generate borrowed items report."""
    output = "\n" + "="*60 + "\n"
    output += "BORROWED ITEMS REPORT".center(60) + "\n"
    output += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(60) + "\n"
    output += "="*60 + "\n\n"
    
    borrowed = [r for r in resources if not r.is_available]
    
    if not borrowed:
        return output + "No items currently borrowed.\n"
    
    data = []
    for r in borrowed:
        status = "OVERDUE" if r.is_overdue() else "On Time"
        data.append([
            r.resource_id,
            r.title[:30],
            r._borrowed_by,
            r._due_date.strftime('%Y-%m-%d') if r._due_date else 'N/A',
            status
        ])
    
    table = tabulate(data,
                    headers=['ID', 'Title', 'Borrower', 'Due Date', 'Status'],
                    tablefmt='grid')
    
    return output + table + f"\n\nTotal Borrowed: {len(borrowed)}\n"


def generate_type_report(resources: List[LibraryResource]) -> str:
    """Generate report by resource type."""
    output = "\n" + "="*60 + "\n"
    output += "RESOURCES BY TYPE REPORT".center(60) + "\n"
    output += "="*60 + "\n\n"
    
    categorized = categorize_by_type(resources)
    
    for resource_type, items in sorted(categorized.items()):
        output += f"\n{resource_type} ({len(items)} items)\n"
        output += "-" * 60 + "\n"
        for item in items:
            status = "Available" if item.is_available else "Borrowed"
            output += f"  • {item.title} by {item.author} - {status}\n"
    
    return output


def generate_borrower_report(borrowers: List[Borrower]) -> str:
    """Generate borrower report."""
    output = "\n" + "="*60 + "\n"
    output += "LIBRARY MEMBERS REPORT".center(60) + "\n"
    output += "="*60 + "\n\n"
    
    if not borrowers:
        return output + "No registered borrowers.\n"
    
    data = []
    for b in borrowers:
        data.append([
            b.borrower_id,
            b.name,
            b.email,
            len(b.borrowed_items)
        ])
    
    table = tabulate(data,
                    headers=['ID', 'Name', 'Email', 'Items Borrowed'],
                    tablefmt='grid')
    
    return output + table + f"\n\nTotal Members: {len(borrowers)}\n"
