# Multi-Database Guide

## Overview

Promethean Light now supports **multiple isolated databases**, enabling you to maintain separate knowledge bases for different purposes: personal data, work projects, HR information, and more.

Each database is completely isolated with its own:
- SQLite database (metadata, tags, clusters)
- Qdrant vector store (embeddings for semantic search)
- Independent search and ML organization

## Why Multiple Databases?

### **Team Collaboration**
- Share project-specific databases with colleagues
- No risk of exposing personal data
- Each engineer can run local queries on shared project data

### **Performance**
- Keep personal database small and fast
- Large project databases don't slow down daily use
- Optimized search within specific contexts

### **Organization**
- Separate concerns (personal vs. work vs. specific projects)
- Different retention policies per database
- Easy archival of completed projects

### **Privacy & Security**
- Personal emails and notes stay private
- Work projects can be shared on network drives
- Clear data boundaries

---

## Database Structure

```
~/.mydata/
├── mydata.db           # Default personal database (SQLite)
├── qdrant/             # Default personal vectors
├── models/             # Shared ML models cache
├── logs/               # Shared logs
├── project_9002/       # Project-specific database
│   ├── mydata.db
│   └── qdrant/
├── project_8750/
│   ├── mydata.db
│   └── qdrant/
└── hr_data/
    ├── mydata.db
    └── qdrant/
```

---

## Using the `--db` Flag

The `--db` flag switches between databases for any command.

### **Default Database (Personal)**
```bash
# These use your default personal database
mydata ask "show me emails from yesterday"
mydata ls
mydata stats
```

### **Project Database**
```bash
# These use the project_9002 database
mydata --db=project_9002 ask "fault level study results"
mydata --db=project_9002 ls
mydata --db=project_9002 stats
```

### **HR Database**
```bash
# These use the hr_data database
mydata --db=hr_data ask "show salary information for India staff"
mydata --db=hr_data search "retention bonus"
```

---

## Database Management Commands

### **1. List All Databases**
```bash
mydata list-dbs
```

**Output:**
```
┌─────────────┬────────────────────────────────┬────────────────┐
│ Name        │ SQLite Path                    │ Status         │
├─────────────┼────────────────────────────────┼────────────────┤
│ default     │ ~/.mydata/mydata.db            │ ✓ SQLite ✓ Qdrant │
│ hr_data     │ ~/.mydata/hr_data/mydata.db    │ ✓ SQLite ✓ Qdrant │
│ project_9002│ ~/.mydata/project_9002/mydata.db│ ✓ SQLite ✓ Qdrant │
└─────────────┴────────────────────────────────┴────────────────┘
```

### **2. Create New Database**
```bash
mydata init project_9002
```

**Output:**
```
✓ Database created: ~/.mydata/project_9002/mydata.db
✓ Vector database initialized: ~/.mydata/project_9002/qdrant

✓ Database 'project_9002' initialized successfully!

Usage examples:
  mydata --db=project_9002 ask "your query"
  mydata --db=project_9002 ls
  mydata --db=project_9002 stats
```

### **3. Ingest into Specific Database**
```bash
# Ingest engineering project into project database
mydata --db=project_9002 ingest "V:\mel_energy_projects\3 CLOSED\9002 WH_FKWKR2"

# Analyze first (dry run)
mydata --db=project_9002 ingest "V:\mel_energy_projects\3 CLOSED\9002 WH_FKWKR2" --dry-run
```

### **4. Query Specific Database**
```bash
# Search in project database
mydata --db=project_9002 ask "protection settings for FKW substation"

# Search in HR database
mydata --db=hr_data ask "who is eligible for retention bonus in Feb 2026?"
```

### **5. View Database Statistics**
```bash
mydata --db=project_9002 stats
```

**Output:**
```
╭─────────────────────────────────────────╮
│ Promethean Light Statistics            │
├─────────────────────────────────────────┤
│ Total Documents: 1,515                  │
│ Total Chunks: 8,432                     │
│ Total Tags: 147                         │
│ Total Clusters: 23                      │
╰─────────────────────────────────────────╯
```

---

## Common Workflows

### **Workflow 1: Personal Knowledge Base (Default)**
```bash
# Use without --db flag for personal data
mydata ask "emails about project deadline"
mydata quick
```

### **Workflow 2: Engineering Project Handover**
```bash
# Step 1: Create project database
mydata init project_9002

# Step 2: Ingest project files
mydata --db=project_9002 ingest "V:\mel_energy_projects\3 CLOSED\9002 WH_FKWKR2"

# Step 3: Query project data
mydata --db=project_9002 ask "what were the main findings of the fault level study?"
mydata --db=project_9002 ask "show me all protection settings"
mydata --db=project_9002 ask "who were the key stakeholders?"

# Step 4: Share database (see TEAM_SHARING_GUIDE.md)
```

### **Workflow 3: HR Data Management**
```bash
# Create HR database
mydata init hr_data

# Ingest HR files
mydata --db=hr_data ingest "V:\mel_energy_office\Business Dev\Staff"

# Query HR data
mydata --db=hr_data ask "show me all India staff with salaries"
mydata --db=hr_data ask "retention bonus expiring in 2026"
```

---

## Database Naming Best Practices

### **Good Names**
- `project_9002` - Clear project identifier
- `hr_data_2025` - Descriptive with context
- `technical_library` - Clear purpose
- `business_dev_proposals` - Departmental scope

### **Avoid**
- `default` - Reserved name
- `models` - Reserved name
- `logs` - Reserved name
- `qdrant` - Reserved name
- `temp` - Not descriptive
- `test123` - Not meaningful

---

## Database Lifecycle

### **Creation**
```bash
mydata init project_9002
```

### **Active Use**
```bash
mydata --db=project_9002 ingest <path>
mydata --db=project_9002 ask <query>
```

### **Archival**
```bash
# Zip database for archival
cd ~/.mydata
tar -czf project_9002_archive_2025-01-21.tar.gz project_9002/

# Or on Windows
powershell Compress-Archive -Path project_9002 -DestinationPath project_9002_archive.zip
```

### **Deletion**
```bash
# Delete database directory
rm -rf ~/.mydata/project_9002

# Or on Windows
rmdir /s /q %USERPROFILE%\.mydata\project_9002
```

---

## Troubleshooting

### **Problem: "Database not found"**
```bash
# Solution: List databases to see available options
mydata list-dbs

# Create if needed
mydata init your_database_name
```

### **Problem: "Wrong database selected"**
```bash
# Check current database by running stats
mydata --db=project_9002 stats

# Use correct --db flag for your data
```

### **Problem: "Slow queries"**
```bash
# Each database is independent - if one is slow, it doesn't affect others
# Check database size
mydata --db=project_9002 stats

# Consider splitting large databases into smaller topic-specific ones
```

---

## Advanced Features

### **Environment Variable Override**
```bash
# Set default database via environment
export MYDATA_DEFAULT_DB=project_9002

# Now all commands use project_9002 by default
mydata ask "query"  # Uses project_9002
```

### **Database Path Override**
```bash
# Use custom location for database home
export MYDATA_HOME=/custom/path/to/mydata

# Databases will be created in /custom/path/to/mydata/
```

---

## Next Steps

- **Learn about document extraction**: See [DOCUMENT_EXTRACTION_GUIDE.md](DOCUMENT_EXTRACTION_GUIDE.md)
- **Share with your team**: See [TEAM_SHARING_GUIDE.md](TEAM_SHARING_GUIDE.md)
- **Engineering handovers**: See [ENGINEERING_HANDOVER_GUIDE.md](ENGINEERING_HANDOVER_GUIDE.md)
- **Safety guarantees**: See [SAFETY_GUARANTEES.md](SAFETY_GUARANTEES.md)
