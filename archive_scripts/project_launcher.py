"""Interactive project launcher for Promethean Light + Claude Code"""

import os
import sys
import subprocess
from pathlib import Path
import inquirer


def scan_projects(projects_dir: Path) -> list:
    """Scan for projects in the projects directory"""
    if not projects_dir.exists():
        print(f"⚠ Projects directory not found: {projects_dir}")
        return []

    # Get all directories in projects folder
    projects = []
    for item in sorted(projects_dir.iterdir()):
        if item.is_dir() and not item.name.startswith('.'):
            projects.append(item.name)

    return projects


def launch_windows_terminal(selected_projects: list, projects_base: Path, promethean_dir: Path):
    """Launch Windows Terminal with multiple tabs for selected projects"""

    if not selected_projects:
        print("ℹ No projects selected")
        return

    print(f"\n🚀 Launching {len(selected_projects)} project(s) in Windows Terminal...")

    # Build Windows Terminal command
    # Format: wt -d "path1" ; new-tab -d "path2" ; new-tab -d "path3" ...

    # First tab - Promethean Light
    wt_cmd = [
        "wt.exe",
        "-w", "0",  # Use existing window or create new
        "-d", str(promethean_dir),
        "cmd.exe", "/k", "echo Promethean Light God Mode && claude"
    ]

    # Add tabs for each selected project
    for project in selected_projects:
        project_path = projects_base / project
        wt_cmd.extend([
            ";", "new-tab",
            "-d", str(project_path),
            "--title", f"📁 {project}",
            "cmd.exe", "/k", f"echo === {project} === && claude"
        ])

    try:
        subprocess.Popen(wt_cmd)
        print("✓ Windows Terminal launched!")
        print("\nProjects opened:")
        print("  • Promethean Light (Tab 1)")
        for i, project in enumerate(selected_projects, 2):
            print(f"  • {project} (Tab {i})")
        print("\n💡 Claude Code is ready in each tab!")

    except FileNotFoundError:
        print("⚠ Windows Terminal not found!")
        print("   Install from: https://aka.ms/terminal")
        print("\n   Falling back to standard cmd windows...")

        # Fallback: Open in separate cmd windows
        for project in selected_projects:
            project_path = projects_base / project
            cmd = f'start "Claude - {project}" cmd /k "cd /d {project_path} && echo === {project} === && claude"'
            os.system(cmd)


def main():
    print("\n" + "="*60)
    print("  PROMETHEAN LIGHT - PROJECT LAUNCHER")
    print("="*60)
    print("\n  Select projects to open in Claude Code")
    print("  • Use ↑↓ to navigate")
    print("  • Space to select/deselect")
    print("  • Enter to launch")
    print("\n" + "="*60 + "\n")

    # Paths
    projects_base = Path("C:/Code/projects")
    promethean_dir = Path("C:/Code/Promethian  Light")

    # Scan projects
    projects = scan_projects(projects_base)

    if not projects:
        print("⚠ No projects found in C:\\Code\\projects")
        input("\nPress Enter to exit...")
        sys.exit(1)

    print(f"Found {len(projects)} project(s):\n")

    # Create checkbox prompt
    questions = [
        inquirer.Checkbox(
            'projects',
            message="Select projects to open (Space to select, Enter to confirm)",
            choices=projects,
        ),
    ]

    try:
        answers = inquirer.prompt(questions)

        if answers is None:  # User cancelled (Ctrl+C)
            print("\n⚠ Cancelled")
            sys.exit(0)

        selected = answers['projects']

        if not selected:
            print("\nℹ No projects selected. Exiting...")
            sys.exit(0)

        # Launch Windows Terminal
        launch_windows_terminal(selected, projects_base, promethean_dir)

    except KeyboardInterrupt:
        print("\n\n⚠ Cancelled")
        sys.exit(0)


if __name__ == "__main__":
    main()
