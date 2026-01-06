# Database-Connected Weekly Checklist Setup Guide

## 🎯 Overview

The new **database-connected** checklist system integrates with your Promethean Light database to:

1. **Auto-populate project names** from the database
2. **Save completed checklists** to the database
3. **Track project health** over time
4. **Search historical checklists** using vector search
5. **Generate analytics** on project trends

---

## 📋 Quick Setup (5 Minutes)

### Step 1: Initialize Database Tables

Run this command once to create the new tables:

```bash
cd "C:\Code\Promethian  Light"
python init_checklist_tables.py
```

This will:
- Create `projects` table
- Create `weekly_checklists` table
- Optionally add sample projects for testing

### Step 2: Start the Daemon

Make sure your Promethean Light daemon is running:

```bash
python -m mydata.daemon
```

The API must be running on `http://localhost:8000` for the checklist to connect.

### Step 3: Open the Database-Connected Checklist

Double-click or open in browser:

```
C:\Code\Promethian  Light\checklists\weekly_client_checklist_db.html
```

You should see:
- 🟢 "Connected to Promethean Light Database" at the top
- Project dropdown populated with your projects
- Client name auto-fills when you select a project

---

## 🆕 New Features

### 1. **Project Dropdown**
- **Auto-populated** from database
- Shows: `Project Name (Client Name)`
- **Client field auto-fills** when project selected
- **Add new projects** via the "+ Add New Project" link

### 2. **Save to Database**
- Click **"💾 Save to Database"** button
- Stores complete checklist in database
- Extracts key metrics (scope changes, concerns, blockers)
- Available for searching and analytics

### 3. **Project Tracking**
- All checklists linked to projects
- View historical checklists per project
- Track health trends over time
- Query using vector search

---

## 📊 Database Schema

### Projects Table
```python
- id: int (auto)
- name: str (indexed)
- client_name: str (indexed)
- project_type: str (Solar, Wind, BESS, Hybrid, Other)
- capacity_mw: float
- status: str (Active, On Hold, Completed, Cancelled)
- start_date: datetime
- target_completion: datetime
- created_at: datetime
- updated_at: datetime
```

### Weekly Checklists Table
```python
- id: int (auto)
- project_id: int (foreign key)
- engineer_name: str (indexed)
- week_ending: datetime (indexed)
- health_rating: str (GREEN, YELLOW, RED)
- checklist_data: JSON (all form fields)
- has_scope_changes: bool
- has_client_concerns: bool
- has_blockers: bool
- on_schedule: bool
- on_budget: bool
- going_well: str
- needs_attention: str
- key_message: str
- created_at: datetime
- updated_at: datetime
```

---

## 🔧 API Endpoints

The system uses these endpoints (auto-created in your API):

### Projects
- `GET /projects` - List all active projects
- `POST /projects` - Create new project
- `GET /projects/{project_id}` - Get project details

### Checklists
- `POST /checklists` - Save completed checklist
- `GET /checklists/{project_id}` - Get all checklists for a project
- `GET /checklists/detail/{checklist_id}` - Get full checklist details

---

## 💡 Usage Workflows

### Workflow 1: Weekly Client Call

1. Open `weekly_client_checklist_db.html`
2. Select project from dropdown → Client auto-fills
3. Fill in engineer name and week ending date
4. Check boxes during the call
5. Fill in summary sections
6. Click **"💾 Save to Database"**
7. Get confirmation: "✅ Checklist saved to database successfully!"

### Workflow 2: Add New Project

**Option A: Via Web Form**
1. Click "+ Add New Project" link
2. Fill in modal form:
   - Project name
   - Client name
   - Project type (Solar, Wind, BESS, etc.)
   - Capacity in MW
3. Click "Create Project"
4. Project instantly appears in dropdown

**Option B: Via Python**
```python
from mydata.database import Database
from mydata.models import Project

db = Database()
session = db.session()

project = Project(
    name="New Solar Project 100MW",
    client_name="Sunshine Energy",
    project_type="Solar",
    capacity_mw=100.0,
    status="Active"
)

session.add(project)
session.commit()
```

**Option C: Via `/save` command**
```
/save PROJECT: Boulder Creek Solar Farm
Client: Boulder Energy Solutions
Type: Solar
Capacity: 50MW
Status: Active
```

### Workflow 3: Search Historical Checklists

Use vector search to find past checklists:

```python
# Search for scope changes across all projects
from mydata.cli import search

results = search("scope change BESS connection")
# Returns checklists mentioning scope changes for BESS projects
```

Or via CLI:
```bash
mydata search "client concerns about timeline"
```

---

## 📈 Analytics & Reporting

### Query Project Health Trends

```python
from mydata.database import Database
from mydata.models import WeeklyChecklist
from sqlmodel import select

db = Database()
session = db.session()

# Get all RED health checklists
stmt = select(WeeklyChecklist).where(
    WeeklyChecklist.health_rating == "RED"
).order_by(WeeklyChecklist.week_ending.desc())

red_projects = session.exec(stmt).all()

for c in red_projects:
    print(f"{c.project.name} - {c.week_ending} - {c.needs_attention}")
```

### Find Projects with Scope Changes

```python
stmt = select(WeeklyChecklist).where(
    WeeklyChecklist.has_scope_changes == True
).order_by(WeeklyChecklist.week_ending.desc())

scope_changes = session.exec(stmt).all()
```

### Client Satisfaction Analysis

```python
# Projects with consistent concerns
from sqlalchemy import func

stmt = select(
    WeeklyChecklist.project_id,
    func.count(WeeklyChecklist.id).label("concern_count")
).where(
    WeeklyChecklist.has_client_concerns == True
).group_by(WeeklyChecklist.project_id).order_by(
    func.count(WeeklyChecklist.id).desc()
)

results = session.exec(stmt).all()
```

---

## 🔍 Vector Search Integration

Your checklists are automatically vectorized and searchable!

**Example Searches:**

```bash
# Find similar project issues
mydata search "network operator delays affecting schedule"

# Find client satisfaction patterns
mydata search "client very happy with communication and progress"

# Find scope change examples
mydata search "client requesting additional BESS capacity analysis"
```

---

## 🚀 Team Rollout

### For Engineers

1. **Bookmark the HTML page:**
   ```
   C:\Code\Promethian  Light\checklists\weekly_client_checklist_db.html
   ```

2. **Fill out after each client call**
   - Select project (dropdown auto-populated)
   - Check boxes as you go
   - Save to database when done

3. **Benefits:**
   - No more lost checklists
   - Auto-populated from projects
   - Searchable history
   - Health tracking over time

### For Project Managers

**Weekly Review Dashboard** (coming soon):
```bash
python -m mydata.checklist_dashboard
```

This will show:
- All projects with health ratings
- Scope changes this week
- Client concerns requiring attention
- Projects going RED

---

## 📝 Migration from Standalone Checklists

If you have existing checklists in HTML/Markdown:

1. **Create the projects first** (via web form or Python)
2. **Use the email generator** to parse old checklists
3. **Import via API**:

```python
import json
from datetime import datetime

# Parse your old checklist
old_checklist_data = {...}  # From email generator

# Create in database
from mydata.models import WeeklyChecklist

checklist = WeeklyChecklist(
    project_id=1,  # Your project ID
    engineer_name="John Smith",
    week_ending=datetime(2025, 11, 21),
    health_rating="GREEN",
    checklist_data=json.dumps(old_checklist_data),
    # ... other fields
)

session.add(checklist)
session.commit()
```

---

## 🛠️ Troubleshooting

### "🔴 Database Offline"
- **Fix:** Start the daemon: `python -m mydata.daemon`
- Check it's running on `http://localhost:8000`
- Test: Open `http://localhost:8000` in browser

### "No projects in dropdown"
- **Fix:** Run `python init_checklist_tables.py` again
- Or add projects via "+ Add New Project" link
- Check database: `sqlite3 mydata/mydata.db "SELECT * FROM projects;"`

### "Save to Database" fails
- Check console (F12) for error messages
- Verify all required fields filled (Project, Engineer, Week Ending, Health)
- Check daemon is running

### Projects not auto-filling
- Clear browser cache and reload
- Check browser console for JavaScript errors
- Verify API connection (status at top of page)

---

## 🎨 Customization

### Change API URL (for remote servers)

Edit `weekly_client_checklist_db.html`:

```javascript
// Change this line:
const API_BASE_URL = 'http://localhost:8000';

// To your server:
const API_BASE_URL = 'http://your-server:8000';
```

### Add Custom Project Fields

Edit `mydata/models.py` → `Project` class:

```python
class Project(SQLModel, table=True):
    # Add your custom fields
    project_manager: Optional[str] = None
    budget_code: Optional[str] = None
    region: Optional[str] = None
```

Then run:
```bash
# Create migration (future)
# For now, recreate database or use ALTER TABLE
```

---

## 📚 Additional Resources

- **Original Checklist Guide:** `WEEKLY_CHECKLIST_GUIDE.md`
- **Quick Reference:** `QUICK_REFERENCE_QUESTIONS.md`
- **Email Generator:** `checklist_email_generator.py`
- **API Docs:** `http://localhost:8000/docs` (when daemon running)

---

## ✨ Future Enhancements

Coming soon:
- 📊 Dashboard to visualize project health trends
- 📧 Auto-email generation from database checklists
- 📈 ML-powered risk prediction
- 🔔 Alerts for projects going from GREEN → YELLOW → RED
- 📱 Mobile app for field engineers
- 🤝 Teams integration

---

## 🆘 Support

Issues? Contact:
- Your PM for process questions
- Dev team for technical issues
- Check logs: `mydata/logs/` (if configured)

---

**Version:** 1.0 (Database-Connected)
**Last Updated:** 2025-11-21
**Requires:** Promethean Light v1.0+
