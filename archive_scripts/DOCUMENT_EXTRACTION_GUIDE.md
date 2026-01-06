# Document Extraction Guide

## Overview

Promethean Light can extract searchable text from common engineering document formats. This guide explains what's supported, how extraction works, and how to troubleshoot issues.

---

## Supported File Formats

### ✅ **Fully Supported** (High Success Rate)

| Format | Extensions | Extraction Method | Typical Success Rate |
|--------|-----------|-------------------|---------------------|
| **Plain Text** | `.txt`, `.log` | Direct UTF-8 decode | ~100% |
| **Markdown** | `.md` | Direct UTF-8 decode | ~100% |
| **CSV** | `.csv` | Direct UTF-8 decode | ~100% |
| **JSON** | `.json` | Direct UTF-8 decode | ~100% |
| **PDF** | `.pdf` | pypdf text extraction | ~85%* |
| **Word** | `.docx` | python-docx extraction | ~95% |
| **Excel** | `.xlsx`, `.xls` | openpyxl extraction | ~90% |

*PDFs with embedded text. Scanned/image-based PDFs require OCR (not yet supported).

### ⚠️ **Partially Supported** (Metadata Only)

| Format | Extensions | What's Indexed | Notes |
|--------|-----------|----------------|-------|
| **CAD Drawings** | `.dwg`, `.dxf` | Filename, path | Full extraction requires AutoCAD API |
| **Images** | `.jpg`, `.png`, `.gif` | Filename, path | OCR support planned |
| **Email** | `.msg`, `.eml` | Not yet | Planned for future release |

### ❌ **Not Supported** (Skipped)

| Format | Extensions | Reason |
|--------|-----------|--------|
| **Executables** | `.exe`, `.dll` | Binary, not document |
| **Archives** | `.zip`, `.7z`, `.rar` | Must be extracted first |
| **Video** | `.mp4`, `.avi`, `.mov` | Media, not document |
| **Audio** | `.mp3`, `.wav` | Media, not document |
| **Engineering Software** | `.psse`, `.pscx`, `.pfd` | Proprietary formats |

---

## Extraction Details by Format

### **📄 PDF Documents**

**How it works:**
- Uses `pypdf` library
- Extracts embedded text from each page
- Combines pages with paragraph breaks

**Success Cases:**
- ✅ Text-based PDFs from Word/LaTeX
- ✅ Reports with selectable text
- ✅ Searchable PDFs from scanning software
- ✅ Forms with text fields

**Failure Cases:**
- ❌ Scanned documents (image-only PDFs)
- ❌ Password-protected PDFs
- ❌ Heavily encrypted PDFs
- ❌ Corrupted PDFs

**Example Output:**
```
=== Page 1 ===
Project Report: 9002 WH_FKWKR2
Fault Level Study

Objectives:
- Calculate fault levels at Wang Hin substation
- Review protection coordination
- Update relay settings

=== Page 2 ===
Methodology:
The fault level study was conducted using PSSE software...
```

**Troubleshooting:**
```bash
# If PDF extraction fails
⚠ No text extracted from PDF (may be scanned/image-based)

# Solutions:
1. Check if PDF is scanned: Open in Adobe Reader, try to select text
2. If scanned: Use OCR software (Adobe Acrobat, ABBYY FineReader)
3. If password-protected: Remove password in Adobe Acrobat
4. If corrupted: Try opening/re-saving in different PDF software
```

---

### **📝 Word Documents (.docx)**

**How it works:**
- Uses `python-docx` library
- Extracts paragraphs in order
- Extracts tables as tab-separated values
- Preserves text structure

**Success Cases:**
- ✅ Modern .docx files (Word 2007+)
- ✅ Reports, specifications, procedures
- ✅ Documents with tables and lists
- ✅ Multi-page technical documents

**Failure Cases:**
- ❌ Old .doc format (Word 97-2003)*
- ❌ Password-protected documents
- ❌ Heavily corrupted files

*Note: .doc (not .docx) requires different library (planned).

**Example Output:**
```
Protection Setting Philosophy

This document describes the protection setting philosophy for the 230kV transmission system.

=== Relay Settings Table ===
Relay ID	Type	Setting	Value
R101	Distance	Zone 1	80%
R101	Distance	Zone 2	120%
R101	Distance	Zone 3	200%
```

**Troubleshooting:**
```bash
# If DOCX extraction fails
⚠ DOCX extraction failed: zipfile.BadZipFile

# Solutions:
1. Open document in Microsoft Word
2. Save As > New File
3. Try extracting the new file

# For .doc (old format)
1. Open in Word
2. Save As > Word Document (.docx)
3. Extract the .docx version
```

---

### **📊 Excel Spreadsheets (.xlsx, .xls)**

**How it works:**
- Uses `openpyxl` library
- Extracts each sheet separately
- Converts cells to tab-separated text
- Includes sheet names as headers

**Success Cases:**
- ✅ Modern .xlsx files (Excel 2007+)
- ✅ Calculation sheets
- ✅ Equipment lists
- ✅ Test results tables

**Failure Cases:**
- ❌ Password-protected workbooks
- ❌ Heavily formatted/complex sheets
- ❌ Sheets with broken links
- ❌ Binary .xlsb format

**Example Output:**
```
=== Sheet: Fault Levels ===
Bus	Voltage	Three-Phase Fault	Single-Phase Fault
WH-230	230kV	25.4 kA	21.2 kA
KR2-230	230kV	28.9 kA	24.1 kA
FKW-115	115kV	18.2 kA	15.7 kA

=== Sheet: Equipment List ===
Tag	Description	Manufacturer	Model
CB-101	Circuit Breaker	ABB	HPL 245
TR-101	Transformer	Siemens	3WE 250MVA
```

**Troubleshooting:**
```bash
# If Excel extraction is slow
🔍 Slow file detected: Protection_Study_Complete.xlsx
  Processing time: 45.2s (expected: ~2s)
  File size: 28 MB (134 sheets, 2.3M cells)
  💡 Suggestion: Consider splitting into separate workbooks

# Solutions:
1. Split large workbooks into smaller files
2. Remove unused sheets
3. Clear unnecessary formatting
```

---

### **📋 Plain Text Files**

**How it works:**
- Direct UTF-8 decoding
- Fallback to Latin-1 if UTF-8 fails
- Preserves original formatting

**Success Cases:**
- ✅ `.txt` - Plain text files
- ✅ `.md` - Markdown documents
- ✅ `.log` - Log files
- ✅ `.csv` - Comma-separated values
- ✅ `.json` - JSON data

**Failure Cases:**
- ❌ Binary files with .txt extension
- ❌ Exotic character encodings (rare)

---

## Extraction Statistics

During ingestion, you'll see detailed statistics about extraction success:

```
┌─────────────────────┬───────────┬──────────┬─────────────┐
│ Status              │ Files     │ Size     │ Success %   │
├─────────────────────┼───────────┼──────────┼─────────────┤
│ ✓ Successfully      │ 1,428     │ 892 MB   │ 94.3%       │
│ ⚠ Partial (errors)  │ 87        │ 34 MB    │ 5.7%        │
│ ✗ Failed/Skipped    │ 1,021     │ 665 MB   │ n/a         │
│ ⏳ Remaining        │ 711       │ 314 MB   │ -           │
└─────────────────────┴───────────┴──────────┴─────────────┘
```

**Interpreting Results:**
- **Successfully**: Full text extracted, ingested into database
- **Partial (errors)**: Some pages/sheets failed, but partial data extracted
- **Failed/Skipped**: Unsupported format, corrupted, or binary files
- **Remaining**: Still being processed

---

## Common Extraction Issues

### **Issue 1: Scanned PDF (No Text)**

**Symptom:**
```
⚠ No text extracted from PDF (may be scanned/image-based)
```

**Cause:** PDF contains only images, no selectable text.

**Solution Options:**

**A. Use OCR Software**
1. Adobe Acrobat Pro: Tools > Recognize Text > In This File
2. ABBYY FineReader: Open > Recognize > Save as Searchable PDF
3. Online: Use Smallpdf, iLovePDF with OCR

**B. Request Source Document**
- Ask for original Word/Excel files before PDF conversion

**C. Manual Transcription (last resort)**
- For critical documents, manually type key information into text file

---

### **Issue 2: Password-Protected Files**

**Symptom:**
```
⚠ Error extracting: file.pdf
  Error: PDF is password protected
  Suggestion: Use Adobe Acrobat to remove password
```

**Solution:**
1. Open file in native application (Adobe, Word, Excel)
2. Enter password
3. Save As > New file without password
4. Re-run ingestion

**Note:** Promethean Light never attempts to crack passwords.

---

### **Issue 3: Old File Formats (.doc, .xls)**

**Symptom:**
```
⚠ Skipping unsupported file: report.doc
```

**Cause:** Old Office formats require different libraries.

**Solution:**
1. Open in Microsoft Office
2. Save As > Choose new format (.docx, .xlsx)
3. Re-run ingestion

**Bulk Conversion (PowerShell):**
```powershell
# Convert all .doc to .docx in a folder
Get-ChildItem -Filter "*.doc" -Recurse | ForEach-Object {
    $word = New-Object -ComObject Word.Application
    $doc = $word.Documents.Open($_.FullName)
    $docx = $_.FullName -replace "\.doc$", ".docx"
    $doc.SaveAs($docx, 16)  # 16 = wdFormatXMLDocument
    $doc.Close()
}
$word.Quit()
```

---

### **Issue 4: Corrupted Files**

**Symptom:**
```
⚠ DOCX extraction failed: zipfile.BadZipFile
⚠ Excel extraction failed: Invalid file format
```

**Cause:** File corruption from incomplete downloads, disk errors, or crashes.

**Solution:**
1. Try opening in native application
2. If it opens: Save As > New file
3. If it doesn't open: Try recovery tools
   - Word: Word > File > Open > Open and Repair
   - Excel: Excel > File > Open > Open and Repair
4. If still fails: Request clean copy from source

---

### **Issue 5: Very Large Files**

**Symptom:**
```
🔍 Slow file detected: Calculations.xlsx
  Processing time: 45.2s (expected: ~2s)
  File size: 28 MB (134 sheets, 2.3M cells)
```

**Impact:** Slows down ingestion, may cause memory issues.

**Solution:**
- **Split Files**: Divide into smaller topical files
- **Remove Unused Sheets**: Delete worksheet tabs with old/unused data
- **Accept Slow Processing**: Sometimes unavoidable for comprehensive data

---

## Optimizing Extraction Success

### **Before Ingestion**

**1. Organize Files**
```
Project/
├── 01_Reports/          # PDFs, Word docs
├── 02_Calculations/     # Excel spreadsheets
├── 03_Correspondence/   # Emails (exported as .txt)
├── 04_Drawings/         # CAD (will be skipped, that's OK)
└── 05_Photos/           # Images (will be skipped, that's OK)
```

**2. Convert to Supported Formats**
- Old .doc → .docx
- Scanned PDFs → OCR-processed PDFs
- Email .msg → Export to .txt or .eml

**3. Clean Up Project Folder**
- Remove duplicate files
- Delete temporary files (~$.docx, *.tmp)
- Remove backup files (*.bak)

### **During Ingestion**

**Use `--dry-run` first:**
```bash
mydata --db=project_9002 ingest "path/to/project" --dry-run
```

**Review the analysis:**
- Check extractable percentage (aim for >60%)
- Identify problem file types
- Fix issues before full ingestion

### **After Ingestion**

**Check Error Report:**
```
Errors (87):
┌──────────────────────────────────┬─────────────────────────┐
│ File                             │ Error                   │
├──────────────────────────────────┼─────────────────────────┤
│ Design_Review_Old.doc            │ Unsupported format      │
│ Scanned_Report.pdf               │ No text (image-based)   │
│ Calculations_Master.xlsx         │ Password protected      │
└──────────────────────────────────┴─────────────────────────┘
```

**Fix Top Issues:**
1. Convert unsupported formats
2. OCR scanned PDFs
3. Remove passwords
4. Re-run for fixed files:
   ```bash
   mydata --db=project_9002 ingest "path/to/fixed_files"
   ```

---

## Extraction Performance

### **Typical Speeds**

| File Type | Typical Speed | Notes |
|-----------|---------------|-------|
| Text files | 50-100 files/sec | Very fast |
| PDF (10 pages) | 2-5 files/sec | Depends on complexity |
| DOCX (20 pages) | 3-8 files/sec | Fast extraction |
| XLSX (10 sheets) | 1-4 files/sec | Varies with sheet size |
| Large PDFs (100+ pages) | 0.5-1 files/sec | Slower |

### **Example Timeline: 2,226 Files**

```
File Type Distribution:
- 1,247 PDFs (avg 15 pages): ~8 minutes
- 456 DOCX (avg 10 pages): ~2 minutes
- 289 XLSX (avg 5 sheets): ~2 minutes
- 234 TXT/CSV: ~30 seconds

Total Estimated Time: ~12-15 minutes
```

**Live Progress:**
```
Processing: ━━━━━━━━━━━━━━━━━━╺━━━━ 68% | 1,515/2,226
Speed: 4.2 files/sec | Elapsed: 6m 12s | Remaining: ~3m 45s
```

---

## Advanced: Custom Extraction

### For Unsupported Formats

If you have files in formats not yet supported, you can:

**Option 1: Pre-convert**
```bash
# Convert CAD to PDF (AutoCAD)
accoreconsole.exe /i drawing.dwg /s export_to_pdf.scr

# Then ingest the PDFs
mydata --db=project_9002 ingest "path/to/converted_pdfs"
```

**Option 2: Export to Text**
```bash
# Open in native application, export as TXT
# Then ingest the text files
```

**Option 3: Request Feature**
- Submit issue on GitHub with file format and use case
- We prioritize based on user needs

---

## File Format Roadmap

### **Coming Soon**
- 📧 Email (.msg, .eml) extraction
- 🖼️ OCR for scanned PDFs
- 📊 Old Office formats (.doc, .xls support)

### **Under Consideration**
- 🎨 Image OCR (.jpg, .png text recognition)
- 📐 CAD metadata extraction
- 📧 Direct Outlook integration (PST files)

### **Submit Requests**
Have a format you need? Let us know!

---

## Next Steps

- **Safety information**: See [SAFETY_GUARANTEES.md](SAFETY_GUARANTEES.md)
- **Multi-database usage**: See [MULTI_DATABASE_GUIDE.md](MULTI_DATABASE_GUIDE.md)
- **Engineering handovers**: See [ENGINEERING_HANDOVER_GUIDE.md](ENGINEERING_HANDOVER_GUIDE.md)
- **Team sharing**: See [TEAM_SHARING_GUIDE.md](TEAM_SHARING_GUIDE.md)
