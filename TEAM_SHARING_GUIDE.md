# Team Sharing Guide

## Overview

Promethean Light's multi-database architecture is designed for **team collaboration**. This guide explains how to share project databases with colleagues so they can instantly search and query project knowledge without re-ingesting.

---

## Why Share Databases?

### **Traditional Engineering Knowledge Sharing** ❌
- Schedule meetings with project engineer
- Wait for their availability
- Hope they remember details
- Get incomplete information
- Repeat for each new question

### **Promethean Light Database Sharing** ✅
- Copy database folder to shared location
- Team members query 24/7
- Instant, comprehensive answers
- No dependency on original engineer
- Self-service knowledge access

---

## Sharing Methods

### **Method 1: Network Drive (Recommended)**

Best for corporate environments with file servers.

#### **Setup (One-Time)**

**Step 1:** Create shared folder on network
```bash
# IT Admin creates shared folder
\\fileserver\engineering\promethean_databases\
```

**Step 2:** Set permissions
```
Folder: \\fileserver\engineering\promethean_databases\
Permissions:
  - Engineering Team: Read, List
  - Project Engineers: Read, Write
  - IT Admins: Full Control
```

#### **Publishing a Database**

**Engineer A (Project owner):**
```bash
# Copy database to network share
xcopy /E /I "%USERPROFILE%\.mydata\project_9002" "\\fileserver\engineering\promethean_databases\project_9002"

# Or on Linux/Mac
cp -r ~/.mydata/project_9002 /mnt/fileserver/engineering/promethean_databases/
```

**Email team:**
```
Subject: Project 9002 Knowledge Base Now Available

The Project 9002 WH_FKWKR2 database is now available for query.

To use:
1. Copy database: \\fileserver\engineering\promethean_databases\project_9002
   To your local: %USERPROFILE%\.mydata\project_9002

2. Query instantly:
   mydata --db=project_9002 ask "your question"

No ingestion needed - ready to use immediately!
```

#### **Accessing a Shared Database**

**Engineer B (Team member):**
```bash
# Copy database from network to local machine
xcopy /E /I "\\fileserver\engineering\promethean_databases\project_9002" "%USERPROFILE%\.mydata\project_9002"

# Verify it's available
mydata list-dbs

# Start querying
mydata --db=project_9002 ask "what was the protection philosophy?"
```

**That's it!** No setup, no ingestion, instant queries.

---

### **Method 2: USB Drive**

Best for air-gapped environments or offline transfer.

**Step 1:** Copy database to USB
```bash
# Insert USB drive (e.g., D:)
xcopy /E /I "%USERPROFILE%\.mydata\project_9002" "D:\project_9002"
```

**Step 2:** Transfer to colleague

**Step 3:** Colleague copies to their machine
```bash
xcopy /E /I "D:\project_9002" "%USERPROFILE%\.mydata\project_9002"
```

**Step 4:** Query immediately
```bash
mydata --db=project_9002 ask "show me fault level results"
```

---

### **Method 3: Compressed Archive**

Best for email sharing or archival.

**Step 1:** Compress database
```bash
# Windows (PowerShell)
Compress-Archive -Path "$env:USERPROFILE\.mydata\project_9002" -DestinationPath "project_9002_db.zip"

# Linux/Mac
tar -czf project_9002_db.tar.gz ~/.mydata/project_9002/
```

**Step 2:** Share archive
- Email (if size permits)
- Upload to SharePoint/OneDrive
- Internal file transfer service

**Step 3:** Recipient extracts
```bash
# Windows
Expand-Archive -Path "project_9002_db.zip" -DestinationPath "$env:USERPROFILE\.mydata"

# Linux/Mac
tar -xzf project_9002_db.tar.gz -C ~/.mydata/
```

**Step 4:** Query
```bash
mydata --db=project_9002 ask "your question"
```

---

### **Method 4: Direct Network Access** (Advanced)

Best for read-only reference by multiple users simultaneously.

**Setup:** Database stays on network drive, users query directly.

**Pros:**
- No local disk space used
- Always up-to-date
- Single source of truth

**Cons:**
- Slower queries (network latency)
- Requires network connection
- Higher network traffic

**Configuration:**
```bash
# Set environment variable to use network path
export MYDATA_HOME="\\fileserver\engineering\promethean_databases"

# Query directly from network
mydata --db=project_9002 ask "your question"
```

---

## Database Size Considerations

### **Typical Database Sizes**

| Project Type | Source Files | Database Size | Ratio |
|-------------|--------------|---------------|-------|
| Small Project | 500 MB | 150-200 MB | ~30-40% |
| Medium Project | 2 GB | 500-800 MB | ~25-40% |
| Large Project | 10 GB | 2-4 GB | ~20-40% |

**Why smaller?**
- Text content only (no embedded images/media)
- Binary files excluded
- Deduplication of similar content

### **Transfer Time Estimates**

| Database Size | Network (1 Gbps) | USB 3.0 | USB 2.0 |
|--------------|------------------|---------|---------|
| 200 MB | ~2 seconds | ~5 seconds | ~20 seconds |
| 800 MB | ~7 seconds | ~15 seconds | ~80 seconds |
| 3 GB | ~25 seconds | ~60 seconds | ~5 minutes |

**Recommendation:** Use network drive for databases >1 GB.

---

## Team Workflows

### **Workflow 1: Project Handover**

**Scenario:** Engineer A worked on project, Engineer B takes over.

**Process:**
1. **Engineer A finalizes database:**
   ```bash
   # Final ingestion
   mydata --db=project_9002 ingest "V:\projects\9002"

   # Verify completeness
   mydata --db=project_9002 stats
   ```

2. **Engineer A shares database:**
   ```bash
   xcopy /E /I "%USERPROFILE%\.mydata\project_9002" "\\network\shared\project_9002"
   ```

3. **Engineer A provides handover notes:**
   ```markdown
   # Project 9002 Handover

   Database: \\network\shared\project_9002

   Key queries to get started:
   - mydata --db=project_9002 ask "project overview"
   - mydata --db=project_9002 ask "outstanding issues"
   - mydata --db=project_9002 ask "key stakeholders"
   ```

4. **Engineer B copies and queries:**
   ```bash
   xcopy /E /I "\\network\shared\project_9002" "%USERPROFILE%\.mydata\project_9002"
   mydata --db=project_9002 ask "what is this project about?"
   ```

---

### **Workflow 2: Team Knowledge Library**

**Scenario:** Multiple engineers need access to historical project data.

**Setup:**
```
\\fileserver\engineering\promethean_databases\
├── project_9002_wh_fkwkr2/
├── project_8750_pea_study/
├── project_8621_rca_failure/
├── project_8455_design_review/
└── README.txt
```

**README.txt:**
```
Promethean Light Shared Databases

Available Databases:
- project_9002: WH/FKW Fault Level Study (2020-2021)
- project_8750: PEA Protection Review (2019-2020)
- project_8621: Transmission Line Failure RCA (2019)
- project_8455: Substation Design Review (2018)

To use:
1. Copy desired database to: %USERPROFILE%\.mydata\
2. Query: mydata --db=<project_name> ask "your question"

For help: contact it@company.com
```

**Team members:**
```bash
# List available databases
dir "\\fileserver\engineering\promethean_databases"

# Copy one they need
xcopy /E /I "\\fileserver\engineering\promethean_databases\project_8750" "%USERPROFILE%\.mydata\project_8750"

# Query immediately
mydata --db=project_8750 ask "show me protection settings"
```

---

### **Workflow 3: Collaborative Project (Active)**

**Scenario:** Multiple engineers working on same live project.

**Approach A: Shared Master Database**
```bash
# One engineer maintains master database
Engineer A: Ingests new documents daily
           Updates shared network copy

# Other engineers sync periodically
Engineers B,C,D: Copy updated database from network weekly
```

**Approach B: Distributed Databases**
```bash
# Each engineer maintains own database
Engineer A: Ingests electrical documents
Engineer B: Ingests civil documents
Engineer C: Ingests commissioning reports

# Share individual databases
Each engineer: Publishes their database to network

# Team members copy all databases
Engineers: Have access to all topical databases
```

---

## Security & Access Control

### **Confidentiality Levels**

#### **Level 1: Public (Team-Wide)**
```
Database: project_9002
Access: All engineering staff
Location: \\fileserver\engineering\shared\
Permissions: Read for all
```

**Example:** Completed projects, general technical knowledge

#### **Level 2: Restricted (Department)**
```
Database: client_xyz_confidential
Access: Project team only
Location: \\fileserver\engineering\restricted\
Permissions: Read for specific group
```

**Example:** Active client projects, sensitive data

#### **Level 3: Private (Individual)**
```
Database: personal (default database)
Access: Individual only
Location: %USERPROFILE%\.mydata\
Permissions: User's home directory
```

**Example:** Personal notes, emails, private data

### **Access Control Best Practices**

**1. Separate Databases by Confidentiality**
```bash
# Don't mix confidential with public data
mydata init project_public       # For sharing
mydata init client_confidential  # Keep private
```

**2. Use Windows/Linux Permissions**
```bash
# Network share permissions control who can access
icacls "\\network\shared\project_9002" /grant "Engineering_Team:(R)"
```

**3. Audit Access**
```bash
# Enable file access auditing on network shares
# IT can monitor who accessed which databases
```

**4. Remove When No Longer Needed**
```bash
# Delete copied databases after project completion
rmdir /s /q "%USERPROFILE%\.mydata\project_9002"
```

---

## Updating Shared Databases

### **Scenario: New Documents Added to Project**

**Option 1: Re-ingest and Republish**
```bash
# Original engineer
mydata --db=project_9002 ingest "V:\projects\9002\06_Additional_Reports"
xcopy /E /I /Y "%USERPROFILE%\.mydata\project_9002" "\\network\shared\project_9002"

# Team notified to update their copies
```

**Option 2: Incremental Sync (Manual)**
```bash
# Share just the new documents
mydata init project_9002_update
mydata --db=project_9002_update ingest "V:\projects\9002\06_Additional_Reports"

# Team copies both databases
xcopy /E /I "\\network\shared\project_9002" "%USERPROFILE%\.mydata\project_9002"
xcopy /E /I "\\network\shared\project_9002_update" "%USERPROFILE%\.mydata\project_9002_update"

# Query both
mydata --db=project_9002 ask "original project data"
mydata --db=project_9002_update ask "new documents"
```

---

## Troubleshooting

### **Issue: Database doesn't appear after copying**

**Check location:**
```bash
# Verify copied to correct path
dir "%USERPROFILE%\.mydata\project_9002"

# Should show:
# mydata.db
# qdrant\
```

**List databases:**
```bash
mydata list-dbs
# Should show project_9002
```

**Solution if missing:**
```bash
# Re-copy ensuring folder structure is correct
xcopy /E /I "\\network\shared\project_9002" "%USERPROFILE%\.mydata\project_9002"
```

---

### **Issue: Queries return no results**

**Check database has data:**
```bash
mydata --db=project_9002 stats
# Should show documents, chunks, etc.
```

**If stats show zero documents:**
- Database copy was incomplete
- Source database was empty
- Re-copy from source

---

### **Issue: Permission denied accessing network**

**Check network permissions:**
```bash
# Test access
dir "\\network\shared\project_9002"

# If access denied:
# Contact IT to grant Read permissions
```

**Workaround:**
- Have colleague with access copy to USB
- Transfer via USB instead

---

### **Issue: Slow queries from network database**

**Symptom:** Queries take 10-30 seconds when querying directly from network.

**Solution:** Copy database locally
```bash
xcopy /E /I "\\network\shared\project_9002" "%USERPROFILE%\.mydata\project_9002"
# Local queries are much faster
```

---

## Advanced: Database Merging

**Scenario:** Multiple engineers created databases for same project, need to combine.

**Currently:** Not directly supported - requires re-ingestion.

**Workaround:**
```bash
# Combine source documents first
mkdir V:\projects\9002_combined
xcopy /E /I V:\projects\9002_part1 V:\projects\9002_combined
xcopy /E /I V:\projects\9002_part2 V:\projects\9002_combined

# Ingest combined source
mydata init project_9002_complete
mydata --db=project_9002_complete ingest "V:\projects\9002_combined"

# Share the complete database
```

**Future Feature:** Database merge tool (planned).

---

## Best Practices Summary

### **✅ Do:**
- ✅ Use descriptive database names (project_9002, not temp_db)
- ✅ Share via network drive for teams
- ✅ Keep source files organized before ingestion
- ✅ Test database works before sharing
- ✅ Provide usage instructions to team
- ✅ Set appropriate network permissions
- ✅ Delete local copies when no longer needed
- ✅ Keep one master copy on network

### **❌ Don't:**
- ❌ Mix personal and shared data in same database
- ❌ Share personal email/notes database
- ❌ Share incomplete or untested databases
- ❌ Give write access to shared databases (read-only)
- ❌ Store only on local machine (no backup)
- ❌ Use for confidential data without access controls

---

## ROI Calculation

### **Traditional Knowledge Transfer**

**Time per handover:**
- Meetings: 4-6 hours
- Documentation: 4-8 hours
- Q&A follow-ups: 2-4 hours
- **Total: 10-18 hours per engineer**

**Cost (assuming $100/hr):**
- **$1,000-1,800 per handover**

### **Promethean Light Knowledge Transfer**

**Time per handover:**
- Initial ingestion: 1-2 hours (one time)
- Database copy: 2-5 minutes
- Self-guided learning: 2-4 hours
- **Total: 2-4 hours (ongoing engineers)**

**Cost:**
- First engineer: $100-200 (ingestion)
- Additional engineers: $200-400 (self-learning)
- **Savings: $600-1,400 per additional engineer**

### **For a 10-Engineer Team**

**Traditional:** $10,000-18,000
**Promethean Light:** $2,000-4,000
**Savings: $6,000-14,000 per project**

---

## Next Steps

- **Multi-database usage**: See [MULTI_DATABASE_GUIDE.md](MULTI_DATABASE_GUIDE.md)
- **Engineering workflows**: See [ENGINEERING_HANDOVER_GUIDE.md](ENGINEERING_HANDOVER_GUIDE.md)
- **Document extraction**: See [DOCUMENT_EXTRACTION_GUIDE.md](DOCUMENT_EXTRACTION_GUIDE.md)
- **Safety information**: See [SAFETY_GUARANTEES.md](SAFETY_GUARANTEES.md)
