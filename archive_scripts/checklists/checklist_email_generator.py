#!/usr/bin/env python3
"""
Weekly Checklist Email Generator

Parses completed WEEKLY_CLIENT_CHECKLIST.md files and generates:
1. Client-facing weekly update emails
2. Management summary emails

Usage:
    python checklist_email_generator.py checklist.md
    python checklist_email_generator.py --all-projects ./checklists/
"""

import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class ChecklistParser:
    """Parse completed weekly client checklists"""

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.data = self._parse_checklist()

    def _parse_checklist(self) -> Dict:
        """Extract data from markdown checklist"""
        with open(self.filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        data = {
            'project': self._extract_field(content, 'Project:'),
            'client': self._extract_field(content, 'Client:'),
            'engineer': self._extract_field(content, 'Engineer:'),
            'week_ending': self._extract_field(content, 'Week Ending:'),
            'health_rating': self._extract_health_rating(content),
            'progress_status': self._extract_checked_items(content, '### Current Work Status'),
            'scope_changes': self._extract_scope_changes(content),
            'technical_issues': self._extract_technical_issues(content),
            'client_satisfaction': self._extract_satisfaction(content),
            'schedule_status': self._extract_checked_items(content, '### Current schedule status'),
            'budget_status': self._extract_checked_items(content, '### Is the project tracking to budget?'),
            'risks': self._extract_section_notes(content, '## 7. RISKS & UPCOMING ISSUES'),
            'action_items': self._extract_actions(content),
            'overall_summary': self._extract_summary(content),
        }

        return data

    def _extract_field(self, content: str, field_name: str) -> str:
        """Extract header field value"""
        pattern = rf'\*\*{re.escape(field_name)}\*\*\s*([^\n]+)'
        match = re.search(pattern, content)
        return match.group(1).strip().replace('_', '').strip() if match else ''

    def _extract_health_rating(self, content: str) -> str:
        """Extract project health rating"""
        section = self._extract_section(content, '## 10. OVERALL PROJECT HEALTH')
        if '- [x] 🟢 Green' in section or '- [X] 🟢 Green' in section:
            return 'GREEN'
        elif '- [x] 🟡 Yellow' in section or '- [X] 🟡 Yellow' in section:
            return 'YELLOW'
        elif '- [x] 🔴 Red' in section or '- [X] 🔴 Red' in section:
            return 'RED'
        return 'UNKNOWN'

    def _extract_checked_items(self, content: str, subsection_header: str) -> List[str]:
        """Extract checked items from a subsection"""
        section = self._extract_subsection(content, subsection_header)
        checked = []
        for line in section.split('\n'):
            if line.strip().startswith('- [x]') or line.strip().startswith('- [X]'):
                item = line.split(']', 1)[1].strip()
                checked.append(item)
        return checked

    def _extract_scope_changes(self, content: str) -> Dict:
        """Extract scope change information"""
        section = self._extract_section(content, '## 2. SCOPE CHANGES & VARIATIONS')

        new_req = self._extract_checked_items(content, '### Has the client mentioned any new requirements?')
        scope_creep = self._extract_checked_items(content, '### Have you identified any scope creep?')
        additional = self._extract_checked_items(content, '### Has the client asked about additional services?')

        # Extract notes
        notes = []
        for line in section.split('\n'):
            if line.startswith('**Description:**') or line.startswith('**Details:**') or line.startswith('**What:**'):
                note = line.split(':', 1)[1].strip().replace('_', '').strip()
                if note:
                    notes.append(note)

        has_changes = (
            any('No changes' not in item for item in new_req) or
            any('No scope creep' not in item for item in scope_creep) or
            any('No additional' not in item for item in additional)
        )

        return {
            'has_changes': has_changes,
            'new_requirements': new_req,
            'scope_creep': scope_creep,
            'additional_services': additional,
            'notes': notes
        }

    def _extract_technical_issues(self, content: str) -> Dict:
        """Extract technical issues and blockers"""
        section = self._extract_section(content, '## 3. TECHNICAL ISSUES & BLOCKERS')

        issues = self._extract_checked_items(content, '### Are there any technical issues affecting progress?')
        data_status = self._extract_checked_items(content, '### Client Data & Information')
        third_party = self._extract_checked_items(content, '### Network Operator / Third Party Issues')

        has_blockers = (
            any('No issues' not in item for item in issues) or
            any('All required data' not in item for item in data_status) or
            any('No third-party' not in item for item in third_party)
        )

        return {
            'has_blockers': has_blockers,
            'issues': issues,
            'data_status': data_status,
            'third_party': third_party
        }

    def _extract_satisfaction(self, content: str) -> Dict:
        """Extract client satisfaction indicators"""
        section = self._extract_section(content, '## 4. CLIENT SATISFACTION')

        satisfied = self._extract_checked_items(content, '### Client seems satisfied with:')
        concerns = self._extract_checked_items(content, '### Client has concerns about:')
        engagement = self._extract_checked_items(content, '### Client engagement level')

        # Extract notes
        positive = self._extract_field_note(section, 'Positive feedback:')
        concern_details = self._extract_field_note(section, 'Specific concerns:')

        has_concerns = any('No concerns' not in item for item in concerns)

        return {
            'satisfied_with': satisfied,
            'concerns': concerns,
            'has_concerns': has_concerns,
            'engagement': engagement,
            'positive_feedback': positive,
            'concern_details': concern_details
        }

    def _extract_actions(self, content: str) -> Dict:
        """Extract action items"""
        section = self._extract_section(content, '## 8. ACTION ITEMS')

        our_team = self._extract_checked_items(content, '### Actions for our team:')
        client = self._extract_checked_items(content, '### Actions for client:')
        third_party = self._extract_checked_items(content, '### Actions for third parties:')

        return {
            'our_team': our_team,
            'client': client,
            'third_party': third_party
        }

    def _extract_summary(self, content: str) -> Dict:
        """Extract overall summary fields"""
        section = self._extract_section(content, '## 10. OVERALL PROJECT HEALTH')

        going_well = self._extract_field_note(section, "What's going well:")
        needs_attention = self._extract_field_note(section, "What needs attention:")
        key_message = self._extract_field_note(section, "Key message for client this week:")

        return {
            'going_well': going_well,
            'needs_attention': needs_attention,
            'key_message': key_message
        }

    def _extract_section(self, content: str, section_header: str) -> str:
        """Extract entire section"""
        pattern = rf'{re.escape(section_header)}(.*?)(?=^## |\Z)'
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        return match.group(1) if match else ''

    def _extract_subsection(self, content: str, subsection_header: str) -> str:
        """Extract subsection"""
        pattern = rf'{re.escape(subsection_header)}(.*?)(?=^### |^## |\Z)'
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        return match.group(1) if match else ''

    def _extract_field_note(self, section: str, field_name: str) -> str:
        """Extract note field from section"""
        pattern = rf'\*\*{re.escape(field_name)}\*\*\s*([^\n*]+)'
        match = re.search(pattern, section)
        value = match.group(1).strip().replace('_', '').strip() if match else ''
        # Get multiple lines if present
        lines = []
        in_field = False
        for line in section.split('\n'):
            if field_name in line:
                in_field = True
                continue
            if in_field:
                if line.strip() and not line.startswith('**'):
                    cleaned = line.replace('_', '').strip()
                    if cleaned:
                        lines.append(cleaned)
                elif line.startswith('**'):
                    break
        return '\n'.join(lines) if lines else value


class EmailGenerator:
    """Generate emails from parsed checklist data"""

    def __init__(self, checklist: ChecklistParser):
        self.data = checklist.data

    def generate_client_email(self) -> str:
        """Generate client-facing weekly update email"""

        # Header
        email = f"Subject: {self.data['project']} - Weekly Update {self.data['week_ending']}\n\n"
        email += f"Hi {self.data['client']},\n\n"
        email += "Quick update on progress this week:\n\n"

        # Key message if present
        if self.data['overall_summary']['key_message']:
            email += f"{self.data['overall_summary']['key_message']}\n\n"

        # What's going well
        email += "WHAT'S GOING WELL\n"
        if self.data['overall_summary']['going_well']:
            for line in self.data['overall_summary']['going_well'].split('\n'):
                if line.strip():
                    email += f"✓ {line.strip()}\n"
        if self.data['client_satisfaction']['satisfied_with']:
            for item in self.data['client_satisfaction']['satisfied_with']:
                email += f"✓ {item}\n"
        email += "\n"

        # What needs attention
        if (self.data['overall_summary']['needs_attention'] or
            self.data['action_items']['client'] or
            self.data['technical_issues']['has_blockers']):
            email += "WHAT NEEDS YOUR ATTENTION\n"

            if self.data['overall_summary']['needs_attention']:
                for line in self.data['overall_summary']['needs_attention'].split('\n'):
                    if line.strip():
                        email += f"• {line.strip()}\n"

            # Client actions
            if self.data['action_items']['client']:
                for action in self.data['action_items']['client']:
                    if 'other' not in action.lower():
                        email += f"• {action}\n"

            # Data/info needed
            if self.data['technical_issues']['data_status']:
                for item in self.data['technical_issues']['data_status']:
                    if 'waiting' in item.lower():
                        email += f"• {item}\n"

            email += "\n"

        # Third party issues (if affecting client)
        if self.data['technical_issues']['third_party']:
            third_party_issues = [item for item in self.data['technical_issues']['third_party']
                                 if 'no third-party' not in item.lower()]
            if third_party_issues:
                email += "EXTERNAL DEPENDENCIES\n"
                for item in third_party_issues:
                    email += f"• {item}\n"
                email += "\n"

        # Scope changes (if any)
        if self.data['scope_changes']['has_changes']:
            email += "SCOPE DISCUSSION ITEMS\n"
            for note in self.data['scope_changes']['notes']:
                if note:
                    email += f"• {note}\n"
            email += "(We can discuss these in more detail if needed)\n\n"

        # Next steps
        email += "NEXT STEPS\n"
        if self.data['action_items']['our_team']:
            email += "Our team:\n"
            for action in self.data['action_items']['our_team']:
                if 'other' not in action.lower():
                    email += f"  - {action}\n"

        email += "\nPlease let me know if you have any questions or concerns.\n\n"
        email += f"Regards,\n{self.data['engineer']}\n"

        return email

    def generate_management_summary(self) -> str:
        """Generate internal management summary"""

        # Health indicator
        health_emoji = {
            'GREEN': '🟢',
            'YELLOW': '🟡',
            'RED': '🔴',
            'UNKNOWN': '⚪'
        }

        summary = f"PROJECT: {self.data['project']}\n"
        summary += f"CLIENT: {self.data['client']}\n"
        summary += f"ENGINEER: {self.data['engineer']}\n"
        summary += f"HEALTH: {health_emoji.get(self.data['health_rating'], '⚪')} {self.data['health_rating']}\n"
        summary += f"WEEK ENDING: {self.data['week_ending']}\n\n"

        # Quick status
        if self.data['progress_status']:
            summary += f"STATUS: {', '.join(self.data['progress_status'])}\n\n"

        # Scope changes (critical for management)
        if self.data['scope_changes']['has_changes']:
            summary += "⚠ SCOPE CHANGES IDENTIFIED:\n"
            for note in self.data['scope_changes']['notes']:
                if note:
                    summary += f"  • {note}\n"
            summary += "\n"

        # Client satisfaction issues
        if self.data['client_satisfaction']['has_concerns']:
            summary += "⚠ CLIENT CONCERNS:\n"
            for concern in self.data['client_satisfaction']['concerns']:
                if 'no concerns' not in concern.lower():
                    summary += f"  • {concern}\n"
            if self.data['client_satisfaction']['concern_details']:
                summary += f"  Details: {self.data['client_satisfaction']['concern_details']}\n"
            summary += "\n"

        # Blockers
        if self.data['technical_issues']['has_blockers']:
            summary += "BLOCKERS:\n"
            for issue in self.data['technical_issues']['issues']:
                if 'no issues' not in issue.lower():
                    summary += f"  • {issue}\n"
            for tp in self.data['technical_issues']['third_party']:
                if 'no third-party' not in tp.lower():
                    summary += f"  • {tp}\n"
            summary += "\n"

        # Wins
        if self.data['overall_summary']['going_well']:
            summary += "WINS:\n"
            for line in self.data['overall_summary']['going_well'].split('\n'):
                if line.strip():
                    summary += f"  ✓ {line.strip()}\n"
            summary += "\n"

        # Support needed
        if self.data['health_rating'] in ['YELLOW', 'RED']:
            summary += "SUPPORT NEEDED:\n"
            if self.data['overall_summary']['needs_attention']:
                for line in self.data['overall_summary']['needs_attention'].split('\n'):
                    if line.strip():
                        summary += f"  • {line.strip()}\n"
            summary += "\n"

        summary += "-" * 60 + "\n"

        return summary


def process_single_checklist(filepath: str):
    """Process a single checklist and generate emails"""
    print(f"\n{'='*60}")
    print(f"Processing: {filepath}")
    print(f"{'='*60}\n")

    parser = ChecklistParser(filepath)
    generator = EmailGenerator(parser)

    print("CLIENT EMAIL")
    print("="*60)
    print(generator.generate_client_email())

    print("\n" + "="*60)
    print("MANAGEMENT SUMMARY")
    print("="*60)
    print(generator.generate_management_summary())


def process_multiple_checklists(directory: str):
    """Process all checklists in a directory"""
    dir_path = Path(directory)
    checklist_files = list(dir_path.glob("*.md"))

    if not checklist_files:
        print(f"No checklist files found in {directory}")
        return

    print(f"\n{'='*60}")
    print(f"WEEKLY MANAGEMENT SUMMARY - ALL PROJECTS")
    print(f"Week Ending: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"{'='*60}\n")

    green_projects = []
    yellow_projects = []
    red_projects = []
    scope_changes = []
    client_issues = []

    for filepath in checklist_files:
        try:
            parser = ChecklistParser(filepath)
            generator = EmailGenerator(parser)
            data = parser.data

            # Categorize by health
            project_name = data['project']
            health = data['health_rating']

            if health == 'GREEN':
                green_projects.append(project_name)
            elif health == 'YELLOW':
                yellow_projects.append(project_name)
            elif health == 'RED':
                red_projects.append(project_name)

            # Collect scope changes
            if data['scope_changes']['has_changes']:
                for note in data['scope_changes']['notes']:
                    if note:
                        scope_changes.append(f"{project_name}: {note}")

            # Collect client issues
            if data['client_satisfaction']['has_concerns']:
                concern_summary = f"{project_name}: "
                concerns = [c for c in data['client_satisfaction']['concerns']
                          if 'no concerns' not in c.lower()]
                concern_summary += ', '.join(concerns)
                if data['client_satisfaction']['concern_details']:
                    concern_summary += f" - {data['client_satisfaction']['concern_details']}"
                client_issues.append(concern_summary)

        except Exception as e:
            print(f"Error processing {filepath}: {e}")

    # Print consolidated summary
    print("PROJECTS OVERVIEW")
    print("-" * 60)
    for proj in green_projects:
        print(f"🟢 {proj}")
    for proj in yellow_projects:
        print(f"🟡 {proj}")
    for proj in red_projects:
        print(f"🔴 {proj}")

    if scope_changes:
        print(f"\n{'SCOPE CHANGES IDENTIFIED'}")
        print("-" * 60)
        for change in scope_changes:
            print(f"• {change}")

    if client_issues:
        print(f"\n{'CLIENT SATISFACTION ALERTS'}")
        print("-" * 60)
        for issue in client_issues:
            print(f"⚠ {issue}")

    print(f"\n{'='*60}")
    print("\nINDIVIDUAL PROJECT DETAILS:")
    print("="*60)

    for filepath in checklist_files:
        try:
            parser = ChecklistParser(filepath)
            generator = EmailGenerator(parser)
            print(generator.generate_management_summary())
        except Exception as e:
            print(f"Error processing {filepath}: {e}\n")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Single checklist:  python checklist_email_generator.py checklist.md")
        print("  Multiple checklists: python checklist_email_generator.py --all-projects ./checklists/")
        sys.exit(1)

    arg = sys.argv[1]

    if arg == '--all-projects':
        if len(sys.argv) < 3:
            print("Please provide directory path")
            sys.exit(1)
        process_multiple_checklists(sys.argv[2])
    else:
        process_single_checklist(arg)


if __name__ == '__main__':
    main()
