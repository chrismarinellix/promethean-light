# War Room Intelligence Dashboard Skill

## Overview

When a user searches for ANY topic (project, person, client, issue, etc.), present the results as a comprehensive "War Room" intelligence dashboard with the following structure:

## Output Format

For every search query, structure the response as follows:

---

### TIMELINE (Visual at top)

```
[Earliest Date] ─────────────────────────────────────────────────── [Latest Date]
     │                           │                          │
     ▼                           ▼                          ▼
  [Event 1]                  [Event 2]                  [Event 3]
  YYYY-MM-DD                 YYYY-MM-DD                 YYYY-MM-DD
  Brief desc                 Brief desc                 Brief desc
```

If more than 5 events, use:
```
TIMELINE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
│
├─ YYYY-MM-DD ─ [Event description]
├─ YYYY-MM-DD ─ [Event description]  ← TODAY marker if relevant
├─ YYYY-MM-DD ─ [Event description]
│
UPCOMING/PENDING ─────────────────────────────────────────────────────────────
├─ YYYY-MM-DD ─ [Upcoming milestone]
└─ YYYY-MM-DD ─ [Deadline/target]
```

---

### PEOPLE INVOLVED

| Person | Role/Title | Organization | Contact | Last Activity |
|--------|-----------|--------------|---------|---------------|
| Name   | Role      | Company      | Email   | Brief context |

Include:
- Key decision makers
- Technical contacts
- Stakeholders
- Anyone mentioned in related documents

---

### KEY TOPICS & THEMES

Extract and categorize the main themes:

**Technical:**
- Topic 1 - brief context
- Topic 2 - brief context

**Commercial:**
- Topic 1 - brief context

**Process/Administrative:**
- Topic 1 - brief context

---

### ACTIONS & TASKS

| Status | Action | Owner | Due/Target | Notes |
|--------|--------|-------|------------|-------|
| 🔴 URGENT | Description | Person | Date | Context |
| 🟡 PENDING | Description | Person | Date | Context |
| 🟢 DONE | Description | Person | Date | Context |
| ⚪ PLANNED | Description | Person | Date | Context |

---

### ISSUES & RISKS

| Severity | Issue | Impact | Mitigation | Status |
|----------|-------|--------|------------|--------|
| 🔴 HIGH | Description | Impact | Action | Status |
| 🟡 MED | Description | Impact | Action | Status |
| 🟢 LOW | Description | Impact | Action | Status |

---

### RELATED DOCUMENTS & SOURCES

| Type | Title/Subject | Date | Key Info |
|------|---------------|------|----------|
| 📧 Email | Subject line | Date | Summary |
| 📄 Document | Title | Date | Summary |
| 📝 Note | Topic | Date | Summary |
| 📊 Data | Description | Date | Summary |

---

### QUICK STATS

```
┌─────────────────────────────────────────────────────────────┐
│ Status: [ACTIVE/PAUSED/COMPLETE]  │ Last Update: YYYY-MM-DD │
├─────────────────────────────────────────────────────────────┤
│ Documents: XX  │ Emails: XX  │ People: XX  │ Actions: XX   │
└─────────────────────────────────────────────────────────────┘
```

---

## How to Use This Skill

1. **Search Promethean Light** for the topic using the API or chatbot
2. **Gather all related data** - emails, documents, notes, projects
3. **Parse and categorize** information into the sections above
4. **Extract dates** to build the timeline
5. **Identify people** and their relationships
6. **Surface actions** - both completed and pending
7. **Highlight risks** and issues requiring attention

## Data Extraction Guidelines

### Finding Timeline Events
Look for:
- Email dates and subjects
- Document creation/modification dates
- Mentioned dates in content ("meeting on March 15", "deadline is April 1")
- Project milestones
- Decision points

### Identifying People
Extract from:
- Email From/To/CC fields
- Document authors
- Names mentioned in content
- Project assignments
- Meeting attendees

### Surfacing Actions
Look for:
- Action items in emails ("please do X", "need to Y")
- Tasks mentioned in notes
- Commitments made
- Deadlines set
- Follow-ups required

### Detecting Issues
Identify:
- Problems mentioned ("issue with", "problem is", "blocker")
- Delays or missed deadlines
- Concerns raised
- Escalations
- Dependencies at risk

## Example Usage

User: "Show me everything about Mt Challenger"

The skill should:
1. Query Promethean Light for "Mt Challenger"
2. Also query for related terms: client name, key people, project code
3. Aggregate all results
4. Parse dates, people, actions, issues
5. Present in War Room format

## Integration with Promethean Light

Use the following to gather data:

```python
# API search
POST /search {"query": "Mt Challenger", "limit": 50}

# Also search for:
# - Related client: "Alinta Energy"
# - Related people: names found in initial results
# - Related project codes: Q7193, etc.
```

Combine results from multiple searches to build comprehensive picture.
