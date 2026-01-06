#!/usr/bin/env python3
"""
Initialize checklist database tables and add sample projects

Run this once to create the Project and WeeklyChecklist tables
and optionally add some sample projects.
"""

import sys
from pathlib import Path

# Add mydata to path
sys.path.insert(0, str(Path(__file__).parent))

from mydata.database import Database
from mydata.models import Project, WeeklyChecklist
from sqlmodel import SQLModel
from datetime import datetime


def init_tables():
    """Create the new tables"""
    print("[*] Initializing checklist database tables...")

    db = Database()
    engine = db.engine

    # Create tables
    SQLModel.metadata.create_all(engine)

    print("[+] Tables created successfully!")
    print("   - projects")
    print("   - weekly_checklists")


def add_sample_projects():
    """Add some sample projects for testing"""
    print("\n[*] Adding sample projects...")

    db = Database()
    session = db.session()

    # Sample projects
    sample_projects = [
        Project(
            name="Solar Farm Connection Study - Boulder Creek 50MW",
            client_name="Boulder Energy Solutions",
            project_type="Solar",
            capacity_mw=50.0,
            status="Active",
            start_date=datetime(2025, 1, 15),
            target_completion=datetime(2025, 6, 30),
        ),
        Project(
            name="Wind Farm Grid Integration - Coastal Winds 100MW",
            client_name="Coastal Wind Developers",
            project_type="Wind",
            capacity_mw=100.0,
            status="Active",
            start_date=datetime(2025, 2, 1),
            target_completion=datetime(2025, 8, 31),
        ),
        Project(
            name="Battery Storage System - Metro BESS 25MW",
            client_name="Metro Energy Storage Ltd",
            project_type="BESS",
            capacity_mw=25.0,
            status="Active",
            start_date=datetime(2025, 3, 1),
            target_completion=datetime(2025, 7, 15),
        ),
        Project(
            name="Hybrid Solar+BESS - Desert Power 75MW",
            client_name="Desert Renewable Energy",
            project_type="Hybrid",
            capacity_mw=75.0,
            status="Active",
            start_date=datetime(2025, 1, 20),
            target_completion=datetime(2025, 9, 30),
        ),
    ]

    for project in sample_projects:
        # Check if project already exists
        existing = session.query(Project).filter(
            Project.name == project.name
        ).first()

        if not existing:
            session.add(project)
            print(f"   [+] Added: {project.name}")
        else:
            print(f"   [-] Skipped (exists): {project.name}")

    session.commit()
    print("\n[+] Sample projects added!")


def show_projects():
    """Display all projects in the database"""
    print("\n[*] Current Projects:")
    print("-" * 80)

    db = Database()
    session = db.session()

    projects = session.query(Project).order_by(Project.name).all()

    if not projects:
        print("   No projects found.")
    else:
        for p in projects:
            print(f"   ID: {p.id}")
            print(f"   Name: {p.name}")
            print(f"   Client: {p.client_name}")
            print(f"   Type: {p.project_type or 'N/A'}")
            print(f"   Capacity: {p.capacity_mw}MW" if p.capacity_mw else "   Capacity: N/A")
            print(f"   Status: {p.status}")
            print("-" * 80)

    print(f"\nTotal Projects: {len(projects)}")


def main():
    """Main function"""
    print("=" * 80)
    print("WEEKLY CHECKLIST DATABASE INITIALIZATION")
    print("=" * 80)

    # Create tables
    init_tables()

    # Ask about sample data
    print("\n")
    response = input("Add sample projects? (y/n): ").lower()
    if response == 'y':
        add_sample_projects()

    # Show current projects
    show_projects()

    print("\n" + "=" * 80)
    print("[+] INITIALIZATION COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Make sure your daemon is running (python -m mydata.daemon)")
    print("2. Open the checklist form:")
    print("   C:\\Code\\Promethian  Light\\checklists\\weekly_client_checklist_db.html")
    print("3. The dropdown will auto-populate with your projects!")
    print("\nTo add more projects:")
    print("- Use the '+ Add New Project' link in the web form")
    print("- Or use the /save command to import project data")
    print()


if __name__ == "__main__":
    main()
