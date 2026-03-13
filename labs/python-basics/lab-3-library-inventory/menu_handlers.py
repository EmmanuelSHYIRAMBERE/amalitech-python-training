#!/usr/bin/env python3
"""
Menu handlers and CLI interface.
"""

import os
from datetime import datetime
from colorama import Fore
from src.models.library_resource import Book, EBook, AudioBook, Borrower
from src.utils.helpers import get_user_input, validate_email, validate_isbn, create_menu, format_date
from src.utils.search import (search_by_title, search_by_author, filter_by_type,
                              filter_available, filter_borrowed, filter_overdue)
from src.utils.reports import (generate_inventory_report, generate_borrowed_report,
                               generate_type_report, generate_borrower_report)
from src.utils.file_io import export_to_text


class MenuHandlers:
    """Handles all menu operations."""
    
    def __init__(self, system):
        self.system = system
    
    def run_main_menu(self):
        """Main application loop."""
        while True:
            print(Fore.YELLOW + "\n" + "="*60)
            print("Library Inventory Management System")
            print("="*60)
            
            options = [
                "Resource Management",
                "Borrower Management",
                "Borrow/Return Operations",
                "Search & Filter",
                "Generate Reports",
                "View Statistics"
            ]
            
            create_menu(options)
            
            choice = get_user_input("Enter your choice: ",
                                   lambda x: x.isdigit() and 0 <= int(x) <= len(options))
            choice = int(choice)
            
            if choice == 0:
                self.system.save_data()
                print(Fore.GREEN + "\nData saved. Goodbye!")
                break
            elif choice == 1:
                self._resource_management_menu()
            elif choice == 2:
                self._borrower_management_menu()
            elif choice == 3:
                self._borrow_return_menu()
            elif choice == 4:
                self._search_filter_menu()
            elif choice == 5:
                self._reports_menu()
            elif choice == 6:
                self._view_statistics()
    
    def _resource_management_menu(self):
        """Resource management submenu."""
        while True:
            print(Fore.CYAN + "\n📚 RESOURCE MANAGEMENT")
            print("="*40)
            
            options = [
                "Add Book",
                "Add EBook",
                "Add AudioBook",
                "View All Resources",
                "View Resource Details",
                "Remove Resource",
                "Back to Main Menu"
            ]
            
            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")
            print("0. Back")
            
            choice = get_user_input("Enter your choice: ",
                                   lambda x: x.isdigit() and 0 <= int(x) <= len(options))
            choice = int(choice)
            
            if choice == 0:
                break
            elif choice == 1:
                self._add_book()
            elif choice == 2:
                self._add_ebook()
            elif choice == 3:
                self._add_audiobook()
            elif choice == 4:
                self._view_all_resources()
            elif choice == 5:
                self._view_resource_details()
            elif choice == 6:
                self._remove_resource()
            
            input("\nPress Enter to continue...")
    
    def _add_book(self):
        """Add a physical book."""
        print(Fore.CYAN + "\n➕ ADD BOOK")
        print("-"*30)
        
        resource_id = get_user_input("Resource ID: ",
                                    lambda x: x not in self.system.resources,
                                    "ID already exists!")
        
        title = get_user_input("Title: ",
                             lambda x: len(x.strip()) >= 2)
        
        author = get_user_input("Author: ",
                              lambda x: len(x.strip()) >= 2)
        
        year = int(get_user_input("Publication Year: ",
                                 lambda x: x.isdigit() and 1000 <= int(x) <= 2100))
        
        isbn = get_user_input("ISBN: ", validate_isbn, "Invalid ISBN!")
        
        pages = int(get_user_input("Number of Pages: ",
                                  lambda x: x.isdigit() and int(x) > 0))
        
        book = Book(resource_id, title, author, year, isbn, pages)
        self.system.add_resource(book)
        print(Fore.GREEN + f"✅ Book '{title}' added successfully!")
    
    def _add_ebook(self):
        """Add an ebook."""
        print(Fore.CYAN + "\n➕ ADD EBOOK")
        print("-"*30)
        
        resource_id = get_user_input("Resource ID: ",
                                    lambda x: x not in self.system.resources)
        
        title = get_user_input("Title: ",
                             lambda x: len(x.strip()) >= 2)
        
        author = get_user_input("Author: ",
                              lambda x: len(x.strip()) >= 2)
        
        year = int(get_user_input("Publication Year: ",
                                 lambda x: x.isdigit() and 1000 <= int(x) <= 2100))
        
        file_size = float(get_user_input("File Size (MB): ",
                                        lambda x: x.replace('.', '').isdigit()))
        
        format_type = get_user_input("Format (PDF/EPUB/MOBI): ",
                                    lambda x: x.upper() in ['PDF', 'EPUB', 'MOBI'])
        
        ebook = EBook(resource_id, title, author, year, file_size, format_type.upper())
        self.system.add_resource(ebook)
        print(Fore.GREEN + f"✅ EBook '{title}' added successfully!")
    
    def _add_audiobook(self):
        """Add an audiobook."""
        print(Fore.CYAN + "\n➕ ADD AUDIOBOOK")
        print("-"*30)
        
        resource_id = get_user_input("Resource ID: ",
                                    lambda x: x not in self.system.resources)
        
        title = get_user_input("Title: ",
                             lambda x: len(x.strip()) >= 2)
        
        author = get_user_input("Author: ",
                              lambda x: len(x.strip()) >= 2)
        
        year = int(get_user_input("Publication Year: ",
                                 lambda x: x.isdigit() and 1000 <= int(x) <= 2100))
        
        duration = int(get_user_input("Duration (minutes): ",
                                     lambda x: x.isdigit() and int(x) > 0))
        
        narrator = get_user_input("Narrator: ",
                                lambda x: len(x.strip()) >= 2)
        
        audiobook = AudioBook(resource_id, title, author, year, duration, narrator)
        self.system.add_resource(audiobook)
        print(Fore.GREEN + f"✅ AudioBook '{title}' added successfully!")
    
    def _view_all_resources(self):
        """View all resources."""
        resources = self.system.get_all_resources()
        
        if not resources:
            print(Fore.YELLOW + "No resources in library.")
            return
        
        print(Fore.CYAN + "\n📚 ALL RESOURCES")
        print("-"*60)
        
        for r in sorted(resources, key=lambda x: x.resource_id):
            print(f"\n{r}")
            print(f"  ID: {r.resource_id} | Type: {r.get_resource_type()}")
            if not r.is_available:
                print(f"  Due: {format_date(r._due_date)}")
                if r.is_overdue():
                    print(Fore.RED + "  ⚠️ OVERDUE")
    
    def _view_resource_details(self):
        """View detailed resource information."""
        if not self.system.resources:
            print(Fore.YELLOW + "No resources in library.")
            return
        
        print(Fore.CYAN + "\n🔍 RESOURCE DETAILS")
        print("-"*30)
        
        for rid, r in self.system.resources.items():
            print(f"{rid}: {r.title}")
        
        resource_id = get_user_input("\nEnter Resource ID: ",
                                    lambda x: x in self.system.resources,
                                    "Resource not found!")
        
        r = self.system.resources[resource_id]
        
        print(Fore.CYAN + "\n" + "="*50)
        print(f"RESOURCE DETAILS: {r.title}")
        print("="*50)
        print(f"ID: {r.resource_id}")
        print(f"Type: {r.get_resource_type()}")
        print(f"Author: {r.author}")
        print(f"Year: {r.year}")
        print(f"Loan Period: {r.get_loan_period()} days")
        print(f"Status: {'Available' if r.is_available else f'Borrowed by {r._borrowed_by}'}")
        
        if not r.is_available:
            print(f"Due Date: {format_date(r._due_date)}")
            if r.is_overdue():
                print(Fore.RED + "⚠️ OVERDUE")
    
    def _remove_resource(self):
        """Remove a resource."""
        if not self.system.resources:
            print(Fore.YELLOW + "No resources in library.")
            return
        
        print(Fore.CYAN + "\n🗑️ REMOVE RESOURCE")
        print("-"*30)
        
        for rid, r in self.system.resources.items():
            print(f"{rid}: {r.title}")
        
        resource_id = get_user_input("\nEnter Resource ID: ",
                                    lambda x: x in self.system.resources)
        
        r = self.system.resources[resource_id]
        confirm = get_user_input(f"Remove '{r.title}'? (y/n): ",
                                lambda x: x.lower() in ['y', 'n'])
        
        if confirm.lower() == 'y':
            self.system.remove_resource(resource_id)
            print(Fore.GREEN + f"✅ Resource removed successfully!")
        else:
            print(Fore.YELLOW + "Operation cancelled.")
    
    def _borrower_management_menu(self):
        """Borrower management submenu."""
        while True:
            print(Fore.CYAN + "\n👥 BORROWER MANAGEMENT")
            print("="*40)
            
            options = [
                "Add Borrower",
                "View All Borrowers",
                "View Borrower Details",
                "Remove Borrower",
                "Back to Main Menu"
            ]
            
            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")
            print("0. Back")
            
            choice = get_user_input("Enter your choice: ",
                                   lambda x: x.isdigit() and 0 <= int(x) <= len(options))
            choice = int(choice)
            
            if choice == 0:
                break
            elif choice == 1:
                self._add_borrower()
            elif choice == 2:
                self._view_all_borrowers()
            elif choice == 3:
                self._view_borrower_details()
            elif choice == 4:
                self._remove_borrower()
            
            input("\nPress Enter to continue...")
    
    def _add_borrower(self):
        """Add a new borrower."""
        print(Fore.CYAN + "\n➕ ADD BORROWER")
        print("-"*30)
        
        borrower_id = get_user_input("Borrower ID: ",
                                    lambda x: x not in self.system.borrowers,
                                    "ID already exists!")
        
        name = get_user_input("Name: ",
                            lambda x: len(x.strip()) >= 2)
        
        email = get_user_input("Email: ", validate_email, "Invalid email!")
        
        borrower = Borrower(borrower_id, name, email)
        self.system.add_borrower(borrower)
        print(Fore.GREEN + f"✅ Borrower '{name}' added successfully!")
    
    def _view_all_borrowers(self):
        """View all borrowers."""
        borrowers = self.system.get_all_borrowers()
        
        if not borrowers:
            print(Fore.YELLOW + "No borrowers registered.")
            return
        
        print(Fore.CYAN + "\n👥 ALL BORROWERS")
        print("-"*50)
        
        for b in sorted(borrowers, key=lambda x: x.borrower_id):
            print(f"\n{b}")
            print(f"  Email: {b.email}")
    
    def _view_borrower_details(self):
        """View borrower details."""
        if not self.system.borrowers:
            print(Fore.YELLOW + "No borrowers registered.")
            return
        
        print(Fore.CYAN + "\n🔍 BORROWER DETAILS")
        print("-"*30)
        
        for bid, b in self.system.borrowers.items():
            print(f"{bid}: {b.name}")
        
        borrower_id = get_user_input("\nEnter Borrower ID: ",
                                    lambda x: x in self.system.borrowers)
        
        b = self.system.borrowers[borrower_id]
        
        print(Fore.CYAN + "\n" + "="*50)
        print(f"BORROWER DETAILS: {b.name}")
        print("="*50)
        print(f"ID: {b.borrower_id}")
        print(f"Email: {b.email}")
        print(f"Items Borrowed: {len(b.borrowed_items)}")
        
        if b.borrowed_items:
            print("\nBorrowed Items:")
            for item_id in b.borrowed_items:
                if item_id in self.system.resources:
                    r = self.system.resources[item_id]
                    print(f"  • {r.title} (Due: {format_date(r._due_date)})")
    
    def _remove_borrower(self):
        """Remove a borrower."""
        if not self.system.borrowers:
            print(Fore.YELLOW + "No borrowers registered.")
            return
        
        print(Fore.CYAN + "\n🗑️ REMOVE BORROWER")
        print("-"*30)
        
        for bid, b in self.system.borrowers.items():
            print(f"{bid}: {b.name}")
        
        borrower_id = get_user_input("\nEnter Borrower ID: ",
                                    lambda x: x in self.system.borrowers)
        
        b = self.system.borrowers[borrower_id]
        
        if b.borrowed_items:
            print(Fore.RED + "Cannot remove borrower with borrowed items!")
            return
        
        confirm = get_user_input(f"Remove '{b.name}'? (y/n): ",
                                lambda x: x.lower() in ['y', 'n'])
        
        if confirm.lower() == 'y':
            self.system.remove_borrower(borrower_id)
            print(Fore.GREEN + f"✅ Borrower removed successfully!")
        else:
            print(Fore.YELLOW + "Operation cancelled.")
    
    def _borrow_return_menu(self):
        """Borrow/return operations menu."""
        while True:
            print(Fore.CYAN + "\n📖 BORROW/RETURN OPERATIONS")
            print("="*40)
            
            options = [
                "Borrow Resource",
                "Return Resource",
                "View Borrowed Items",
                "View Overdue Items",
                "Back to Main Menu"
            ]
            
            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")
            print("0. Back")
            
            choice = get_user_input("Enter your choice: ",
                                   lambda x: x.isdigit() and 0 <= int(x) <= len(options))
            choice = int(choice)
            
            if choice == 0:
                break
            elif choice == 1:
                self._borrow_resource()
            elif choice == 2:
                self._return_resource()
            elif choice == 3:
                self._view_borrowed_items()
            elif choice == 4:
                self._view_overdue_items()
            
            input("\nPress Enter to continue...")
    
    def _borrow_resource(self):
        """Borrow a resource."""
        available = filter_available(self.system.get_all_resources())
        
        if not available:
            print(Fore.YELLOW + "No resources available to borrow.")
            return
        
        print(Fore.CYAN + "\n📖 BORROW RESOURCE")
        print("-"*30)
        
        print("\nAvailable Resources:")
        for r in available:
            print(f"{r.resource_id}: {r.title} by {r.author}")
        
        resource_id = get_user_input("\nEnter Resource ID: ",
                                    lambda x: x in [r.resource_id for r in available])
        
        print("\nBorrowers:")
        for bid, b in self.system.borrowers.items():
            print(f"{bid}: {b.name}")
        
        borrower_id = get_user_input("\nEnter Borrower ID: ",
                                    lambda x: x in self.system.borrowers)
        
        resource = self.system.resources[resource_id]
        borrower = self.system.borrowers[borrower_id]
        
        if resource.borrow(borrower.name):
            borrower.add_borrowed_item(resource_id)
            self.system.save_data()
            print(Fore.GREEN + f"✅ '{resource.title}' borrowed by {borrower.name}")
            print(f"Due date: {format_date(resource._due_date)}")
        else:
            print(Fore.RED + "❌ Failed to borrow resource.")
    
    def _return_resource(self):
        """Return a resource."""
        borrowed = filter_borrowed(self.system.get_all_resources())
        
        if not borrowed:
            print(Fore.YELLOW + "No resources currently borrowed.")
            return
        
        print(Fore.CYAN + "\n📚 RETURN RESOURCE")
        print("-"*30)
        
        print("\nBorrowed Resources:")
        for r in borrowed:
            print(f"{r.resource_id}: {r.title} (Borrowed by {r._borrowed_by})")
        
        resource_id = get_user_input("\nEnter Resource ID: ",
                                    lambda x: x in [r.resource_id for r in borrowed])
        
        resource = self.system.resources[resource_id]
        
        # Find borrower and remove item
        for borrower in self.system.borrowers.values():
            if resource_id in borrower.borrowed_items:
                borrower.remove_borrowed_item(resource_id)
                break
        
        if resource.return_resource():
            self.system.save_data()
            print(Fore.GREEN + f"✅ '{resource.title}' returned successfully!")
        else:
            print(Fore.RED + "❌ Failed to return resource.")
    
    def _view_borrowed_items(self):
        """View all borrowed items."""
        borrowed = filter_borrowed(self.system.get_all_resources())
        
        if not borrowed:
            print(Fore.YELLOW + "No resources currently borrowed.")
            return
        
        print(Fore.CYAN + "\n📖 BORROWED ITEMS")
        print("-"*60)
        
        for r in borrowed:
            print(f"\n{r.title} by {r.author}")
            print(f"  Borrowed by: {r._borrowed_by}")
            print(f"  Due: {format_date(r._due_date)}")
            if r.is_overdue():
                print(Fore.RED + "  ⚠️ OVERDUE")
    
    def _view_overdue_items(self):
        """View overdue items."""
        overdue = filter_overdue(self.system.get_all_resources())
        
        if not overdue:
            print(Fore.GREEN + "No overdue items!")
            return
        
        print(Fore.RED + "\n⚠️ OVERDUE ITEMS")
        print("-"*60)
        
        for r in overdue:
            print(f"\n{r.title} by {r.author}")
            print(f"  Borrowed by: {r._borrowed_by}")
            print(f"  Due: {format_date(r._due_date)}")
    
    def _search_filter_menu(self):
        """Search and filter menu."""
        while True:
            print(Fore.CYAN + "\n🔍 SEARCH & FILTER")
            print("="*40)
            
            options = [
                "Search by Title",
                "Search by Author",
                "Filter by Type",
                "Filter Available",
                "Filter Borrowed",
                "Back to Main Menu"
            ]
            
            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")
            print("0. Back")
            
            choice = get_user_input("Enter your choice: ",
                                   lambda x: x.isdigit() and 0 <= int(x) <= len(options))
            choice = int(choice)
            
            if choice == 0:
                break
            elif choice == 1:
                self._search_by_title()
            elif choice == 2:
                self._search_by_author()
            elif choice == 3:
                self._filter_by_type()
            elif choice == 4:
                self._filter_available()
            elif choice == 5:
                self._filter_borrowed()
            
            input("\nPress Enter to continue...")
    
    def _search_by_title(self):
        """Search resources by title."""
        query = get_user_input("Enter title to search: ")
        results = search_by_title(self.system.get_all_resources(), query)
        
        if not results:
            print(Fore.YELLOW + "No results found.")
            return
        
        print(Fore.CYAN + f"\n🔍 SEARCH RESULTS ({len(results)} found)")
        print("-"*60)
        for r in results:
            print(f"  • {r}")
    
    def _search_by_author(self):
        """Search resources by author."""
        query = get_user_input("Enter author to search: ")
        results = search_by_author(self.system.get_all_resources(), query)
        
        if not results:
            print(Fore.YELLOW + "No results found.")
            return
        
        print(Fore.CYAN + f"\n🔍 SEARCH RESULTS ({len(results)} found)")
        print("-"*60)
        for r in results:
            print(f"  • {r}")
    
    def _filter_by_type(self):
        """Filter resources by type."""
        print("\nResource Types:")
        print("1. Book")
        print("2. EBook")
        print("3. AudioBook")
        
        choice = get_user_input("Select type: ",
                               lambda x: x in ['1', '2', '3'])
        
        type_map = {'1': 'Book', '2': 'EBook', '3': 'AudioBook'}
        resource_type = type_map[choice]
        
        results = filter_by_type(self.system.get_all_resources(), resource_type)
        
        if not results:
            print(Fore.YELLOW + f"No {resource_type}s found.")
            return
        
        print(Fore.CYAN + f"\n📚 {resource_type.upper()}S ({len(results)} found)")
        print("-"*60)
        for r in results:
            print(f"  • {r}")
    
    def _filter_available(self):
        """Show available resources."""
        results = filter_available(self.system.get_all_resources())
        
        if not results:
            print(Fore.YELLOW + "No available resources.")
            return
        
        print(Fore.CYAN + f"\n✅ AVAILABLE RESOURCES ({len(results)} found)")
        print("-"*60)
        for r in results:
            print(f"  • {r}")
    
    def _filter_borrowed(self):
        """Show borrowed resources."""
        results = filter_borrowed(self.system.get_all_resources())
        
        if not results:
            print(Fore.YELLOW + "No borrowed resources.")
            return
        
        print(Fore.CYAN + f"\n📖 BORROWED RESOURCES ({len(results)} found)")
        print("-"*60)
        for r in results:
            print(f"  • {r}")
    
    def _reports_menu(self):
        """Reports menu."""
        while True:
            print(Fore.CYAN + "\n📊 REPORTS")
            print("="*40)
            
            options = [
                "Inventory Report",
                "Borrowed Items Report",
                "Resource Type Report",
                "Borrower Report",
                "Export to Text File",
                "Back to Main Menu"
            ]
            
            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")
            print("0. Back")
            
            choice = get_user_input("Enter your choice: ",
                                   lambda x: x.isdigit() and 0 <= int(x) <= len(options))
            choice = int(choice)
            
            if choice == 0:
                break
            elif choice == 1:
                print(generate_inventory_report(self.system.get_all_resources()))
            elif choice == 2:
                print(generate_borrowed_report(self.system.get_all_resources()))
            elif choice == 3:
                print(generate_type_report(self.system.get_all_resources()))
            elif choice == 4:
                print(generate_borrower_report(self.system.get_all_borrowers()))
            elif choice == 5:
                self._export_report()
            
            input("\nPress Enter to continue...")
    
    def _export_report(self):
        """Export report to text file."""
        os.makedirs('reports', exist_ok=True)
        filename = f"reports/library_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        export_to_text(self.system.get_all_resources(), filename)
        print(Fore.GREEN + f"✅ Report exported to {filename}")
    
    def _view_statistics(self):
        """View library statistics."""
        from src.utils.search import get_statistics
        
        stats = get_statistics(self.system.get_all_resources())
        
        print(Fore.CYAN + "\n📊 LIBRARY STATISTICS")
        print("="*50)
        print(f"📚 Total Resources: {stats['total']}")
        print(f"✅ Available: {stats['available']}")
        print(f"📖 Borrowed: {stats['borrowed']}")
        print(f"⚠️ Overdue: {stats['overdue']}")
        
        print("\n📊 By Type:")
        for resource_type, count in stats['by_type'].items():
            print(f"  • {resource_type}: {count}")
        
        print(f"\n👥 Total Borrowers: {len(self.system.borrowers)}")
        
        input("\nPress Enter to continue...")
