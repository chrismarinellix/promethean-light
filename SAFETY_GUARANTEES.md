# Safety Guarantees: Read-Only Operations

## 🔒 CRITICAL GUARANTEE

**Promethean Light NEVER modifies, moves, or deletes your source files.**

All ingestion operations are **100% READ-ONLY**. Your original files remain completely untouched.

---

## What This Means

### ✅ **What Promethean Light DOES:**
- ✅ **Reads** files from your directories
- ✅ **Extracts** text content from documents
- ✅ **Copies** text data to its own database
- ✅ **Creates** vector embeddings in separate storage
- ✅ **Stores** metadata in SQLite database

### ❌ **What Promethean Light NEVER DOES:**
- ❌ **Never modifies** source file contents
- ❌ **Never renames** source files
- ❌ **Never moves** source files to different locations
- ❌ **Never deletes** source files
- ❌ **Never changes** file permissions or attributes
- ❌ **Never alters** file timestamps
- ❌ **Never writes** any data back to source files

---

## Technical Implementation

### File Reading Process

**1. Open in Read-Only Mode**
```python
# All file operations use read-only mode
content = file_path.read_bytes()  # Read-only, never write
```

**2. Process in Memory**
```python
# Text extraction happens in memory using BytesIO
from io import BytesIO
pdf_file = BytesIO(content)  # Memory buffer, not file modification
```

**3. Store in Separate Database**
```python
# Extracted text goes to Promethean Light's database
# NOT back to the source file
doc = Document(raw_text=text, source=f"file://{file_path}")
db.add(doc)  # Stored in ~/.mydata/, not in source location
```

### No Write Permissions Required

Promethean Light **does not request** and **does not need** write permissions to your project directories.

- Network drives can be read-only
- USB drives can be write-protected
- Source folders can have read-only attributes
- Files can be locked by other processes

**It will still work!**

---

## Verification Methods

### Method 1: Check File Modification Times

**Before Ingestion:**
```bash
# On Windows
dir "V:\mel_energy_projects\3 CLOSED\9002 WH_FKWKR2" /s /t:w > before.txt

# On Linux/Mac
find /path/to/project -type f -exec stat -c "%y %n" {} \; > before.txt
```

**After Ingestion:**
```bash
# On Windows
dir "V:\mel_energy_projects\3 CLOSED\9002 WH_FKWKR2" /s /t:w > after.txt

# Compare
fc before.txt after.txt  # No changes!
```

### Method 2: Hash Verification

**Generate checksums before:**
```bash
# Windows (PowerShell)
Get-ChildItem -Recurse | Get-FileHash | Export-Csv checksums_before.csv

# Linux/Mac
find . -type f -exec md5sum {} \; > checksums_before.txt
```

**Generate checksums after:**
```bash
# Windows (PowerShell)
Get-ChildItem -Recurse | Get-FileHash | Export-Csv checksums_after.csv

# Linux/Mac
find . -type f -exec md5sum {} \; > checksums_after.txt
```

**Compare:** They will be identical!

### Method 3: Set Read-Only Attribute

**Before ingestion, make everything read-only:**
```bash
# Windows
attrib +R /S "V:\mel_energy_projects\3 CLOSED\9002 WH_FKWKR2\*"

# Linux/Mac
chmod -R a-w /path/to/project
```

**Then run ingestion:**
```bash
mydata --db=project_9002 ingest "V:\mel_energy_projects\3 CLOSED\9002 WH_FKWKR2"
```

**Result:** Works perfectly! No error messages about write permissions.

---

## Where Data IS Written

Promethean Light writes data to **only one location**: your Promethean Light data directory.

### Default Location
```
~/.mydata/                          # All Promethean Light data
├── project_9002/                   # Project database
│   ├── mydata.db                   # SQLite database (YOUR COPY of data)
│   └── qdrant/                     # Vector embeddings (YOUR COPY)
├── logs/                           # Application logs
└── models/                         # ML model cache
```

### On Windows
```
C:\Users\<username>\.mydata\
```

### On Linux/Mac
```
/home/<username>/.mydata/
```

**Your source files remain at:**
```
V:\mel_energy_projects\3 CLOSED\9002 WH_FKWKR2\  (untouched!)
```

---

## Safety by Design

### Architecture Principles

**1. Copy-on-Read**
- Text is extracted and copied to database
- Original files are never touched

**2. Separate Storage**
- Database location is completely separate from source files
- No risk of overwriting

**3. No File Handles Kept Open**
- Files are opened, read, and immediately closed
- No locks on source files

**4. Exception Handling**
- If a file can't be read, it's skipped
- No attempts to modify or "fix" the file

**5. Explicit Read-Only APIs**
- All file I/O uses read-only methods
- Write methods are never called on source paths

---

## What About Errors?

### If a File is Corrupted
```
⚠ DOCX extraction failed: zipfile.BadZipFile
⚠ Suggestion: Try opening in Word and saving as new file
```

**Promethean Light:**
- Logs the error
- Skips the file
- Continues with other files
- **Never attempts to "fix" or modify the corrupted file**

### If a File is Password-Protected
```
⚠ Error extracting: file.pdf
  Error: PDF is password protected
  Suggestion: Use Adobe Acrobat to remove password
```

**Promethean Light:**
- Reports the issue
- Skips the file
- **Never tries to break protection or modify the file**

### If Permissions Are Denied
```
✗ Error reading file: Permission denied
```

**Promethean Light:**
- Logs the error
- Moves to next file
- **Never requests elevated permissions**
- **Never modifies file permissions**

---

## Network Drive Safety

### Reading from Network Drives
```bash
# Safe to ingest from network locations
mydata --db=project_9002 ingest "\\network\projects\9002"
```

**Benefits:**
- Network admin can set strict read-only permissions
- Multiple users can ingest simultaneously
- Central file server remains authoritative
- Audit trails show only read operations

### Example Network Setup
```
Server: \\fileserver\projects\9002\
Permissions:
  - Domain Users: Read, List
  - Engineers: Read, List
  - Admin Only: Write, Modify

Promethean Light: Works perfectly with Read permissions only!
```

---

## Compliance & Audit

### For IT Departments

**Q: Does this tool modify source files?**
A: No. All operations are read-only.

**Q: What file permissions are required?**
A: Read and List permissions only.

**Q: Where is data stored?**
A: User's home directory (~/.mydata/), not in project folders.

**Q: Can we audit file access?**
A: Yes. Enable Windows/Linux file access auditing. You'll see only READ operations.

**Q: What if files are on write-protected media?**
A: Works perfectly. USB drives can be write-protected.

**Q: Can network admins monitor this?**
A: Yes. Standard file server logs will show read-only access.

---

## Developer Code Audit

For technical verification, here's where to look in the source code:

### ingestion.py
```python
Line 41: content = file_path.read_bytes()  # Read-only
Line 232-352: _extract_text_from_file()    # Only reads, never writes
```

### bulk_ingest.py
```python
Line 87: all_files = list(directory_path.rglob("*"))  # Read-only scan
Line 238: content = file_path.read_bytes()            # Read-only
Line 242: text = pipeline._extract_text_from_file()   # Read-only extraction
```

### No write operations in:
- `ingestion.py` - No write calls to source paths
- `bulk_ingest.py` - No write calls to source paths
- `cli.py` - ingest command only reads
- All file extraction methods use `BytesIO` (memory buffers)

---

## Legal & Professional Use

### For Engineering Consultancies

**Promethean Light is safe for use with client data because:**

1. **No Data Modification**
   - Client files remain pristine
   - Meets "do not alter client data" policies

2. **Audit Trail**
   - System logs show read-only operations
   - Complies with ISO 9001 quality management

3. **Confidentiality**
   - Data stays on your machine (or approved server)
   - No external API calls for document processing
   - 100% local ML models

4. **Reproducibility**
   - Original files unchanged
   - Can re-run analysis anytime
   - Meets engineering documentation standards

---

## Emergency Recovery

### If You're Still Worried

**Option 1: Work on a Copy**
```bash
# Make a complete copy of the project
cp -r /original/project /temp/project_copy

# Ingest from the copy
mydata --db=project_9002 ingest /temp/project_copy

# Original is 100% safe, copy can be deleted after
```

**Option 2: Read-Only Mount**
```bash
# On Linux, mount read-only
mount -o ro /dev/sdb1 /mnt/project

# Ingest from read-only mount
mydata --db=project_9002 ingest /mnt/project
```

**Option 3: Use File System Snapshots**
```bash
# Windows: Volume Shadow Copy
# Linux: LVM snapshots
# ZFS: zfs snapshot

# Take snapshot before ingestion
# Verify nothing changed
# Remove snapshot
```

---

## Frequently Asked Questions

### Q: What if I accidentally interrupt ingestion with Ctrl+C?
**A:** Source files remain untouched. Only the Promethean Light database may be incomplete. Re-run ingestion to complete.

### Q: Can malware spread through ingestion?
**A:** No. Text extraction doesn't execute code. PDFs and Office docs are parsed, not opened in their native applications.

### Q: What about macro-enabled Excel files?
**A:** Macros are NOT executed. Only cell values are extracted as text.

### Q: Can ingestion damage files on a failing hard drive?
**A:** Reading from a failing drive has the same risk as any read operation (e.g., opening a file). Promethean Light doesn't increase risk beyond normal file access.

### Q: Does ingestion fragment files?
**A:** No. Files are read sequentially without seeking, minimizing I/O.

### Q: Can I ingest while others are editing files?
**A:** Yes, but you may get incomplete data from files currently being written. Best practice: ingest from closed/completed projects.

---

## Certification

**We, the developers of Promethean Light, certify that:**

1. ✅ All file ingestion operations are read-only
2. ✅ No source file modification code exists
3. ✅ No file deletion code exists
4. ✅ No file moving/renaming code exists
5. ✅ All extracted data is stored separately
6. ✅ Source code is available for audit
7. ✅ Users can verify with checksums
8. ✅ Write-protected media works correctly

**Your files are safe.**

---

## Next Steps

- **Learn about document types**: See [DOCUMENT_EXTRACTION_GUIDE.md](DOCUMENT_EXTRACTION_GUIDE.md)
- **Share databases safely**: See [TEAM_SHARING_GUIDE.md](TEAM_SHARING_GUIDE.md)
- **Engineering workflows**: See [ENGINEERING_HANDOVER_GUIDE.md](ENGINEERING_HANDOVER_GUIDE.md)
- **Multi-database usage**: See [MULTI_DATABASE_GUIDE.md](MULTI_DATABASE_GUIDE.md)
