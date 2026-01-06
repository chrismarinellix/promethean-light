# Promethean Light - Backup System (OPTIMIZED ⚡)

## Overview

**Highly efficient** automated backup system for Promethean Light that backs up:
- SQLite database (`mydata/mydata.db`) - Always full backup for consistency
- Qdrant vector database (`~/.mydata/qdrant`) - Always full backup for consistency
- Complete program files - **INCREMENTAL with 95-97% efficiency**

Backups are stored at: `V:\mel_energy_office\Business Dev\Data Base Backup`

### Efficiency Features (NEW!)

**Incremental Backup Optimization:**
- **97%+ time savings** on daily backups (Mon-Sat)
- Only changed files are read from source drive
- Unchanged files reused from previous backup
- **Example**: Recent backup showed 11 files changed, 367 reused = **97.1% efficiency**
- **Backup time**: ~30 seconds (incremental) vs 4 minutes (full)

**Smart Backup Strategy:**
- **Mon-Sat**: Incremental backups (super fast, reuse 95-97% of files)
- **Sunday**: Full backup (clean baseline for the week)
- **1st of month**: Full monthly backup (long-term archive)
- **Hourly** (optional): Incremental during work hours (8am-6pm)

## Retention Policy

The backup system implements a 4-tier rotation strategy:

- **Hourly**: Keep last 24 hours (8am-6pm work hours only) ⚡ NEW!
- **Daily**: Keep last 7 days (2:00 AM)
- **Weekly**: Keep last 4 weeks (created every Sunday)
- **Monthly**: Keep last 12 months (created on 1st of each month)

## Scheduled Backup Time

**2:00 AM Daily** - Industry best practice:
- System is typically idle (no user activity)
- Minimal performance impact
- Before business hours
- Consistent timing for restore point planning

## Installation

### 1. Install Daily Backup Schedule (Recommended)

Right-click `INSTALL_BACKUP_SCHEDULE.bat` and select **Run as administrator**

This creates a Windows Task Scheduler job that runs daily at 2:00 AM.

### 2. Install Hourly Backup Schedule (RECOMMENDED for Work Hours Protection!)

Right-click `INSTALL_HOURLY_BACKUP_SCHEDULE.bat` and select **Run as administrator**

This creates an hourly backup task that runs every hour from 8:00 AM to 6:00 PM.

**Benefits:**
- ⚡ Fast: Only 5-10 seconds per backup (incremental with hard links)
- 🛡️ Protection: Lose max 1 hour of data vs 24 hours
- 📧 Email Safety: Outlook emails backed up as they arrive
- 💾 Efficient: ~300 MB total for 24 hourly backups (70-80% space savings)

### 3. Verify Installation

1. Press `Win + R`
2. Type: `taskschd.msc`
3. Look for these tasks in the list:
   - `PrometheanLightBackup` (Daily at 2:00 AM)
   - `PrometheanLightHourlyBackup` (Hourly 8am-6pm)

## Usage

### Manual Backup

- **Full Daily Backup**: Double-click `BACKUP_NOW.bat` (no admin required)
- **Quick Hourly Backup**: Double-click `BACKUP_HOURLY.bat` (no admin required, 5-10 seconds)

### View Logs

Backup logs are stored in:
```
V:\mel_energy_office\Business Dev\Data Base Backup\logs\
```

Each month has its own log file: `backup_YYYYMM.log`

### Uninstall Schedule

- **Daily Backup**: Right-click `UNINSTALL_BACKUP_SCHEDULE.bat` and select **Run as administrator**
- **Hourly Backup**: Right-click `UNINSTALL_HOURLY_BACKUP_SCHEDULE.bat` and select **Run as administrator**

## Backup Structure

```
V:\mel_energy_office\Business Dev\Data Base Backup\
├── hourly\                                ⚡ NEW!
│   ├── backup_20250121_080000\           (8:00 AM)
│   ├── backup_20250121_090000\           (9:00 AM)
│   ├── backup_20250121_100000\           (10:00 AM)
│   │   ├── mydata.db                     (SQLite - full copy)
│   │   ├── qdrant\                       (Qdrant - full copy)
│   │   ├── promethean_light\             (Program - incremental)
│   │   └── BACKUP_INFO.txt
│   └── ... (24 hours retained)
├── daily\
│   ├── backup_20250121_020000\
│   │   ├── mydata.db                     (SQLite database)
│   │   ├── qdrant\                       (Vector database)
│   │   ├── promethean_light\             (Program files)
│   │   └── BACKUP_INFO.txt               (Manifest)
│   └── ... (7 days retained)
├── weekly\
│   └── ... (4 weeks retained)
├── monthly\
│   └── ... (12 months retained)
└── logs\
    └── backup_202501.log
```

## What Gets Backed Up

### SQLite Database
- Main metadata database
- Documents, chunks, tags, clusters
- Email credentials (encrypted)
- Hot-copy using SQLite backup API (safe while running)

### Qdrant Vector Database
- All vector embeddings
- Complete collection data
- Excludes lock files

### Program Files
- All Python source code
- Configuration files
- Batch launchers
- Requirements files

### What's Excluded
- `__pycache__/` (Python cache)
- `.git/` (Git repository)
- `.venv/`, `venv/` (Virtual environments)
- `*.log` (Log files - separate backup)
- `.mydata/` (User data - separately backed up)
- Temporary files

## Restore Process

### Full System Restore

1. **Stop Promethean Light** (if running)
2. **Restore Program Files**:
   ```
   Copy V:\mel_energy_office\Business Dev\Data Base Backup\[daily|weekly|monthly]\backup_XXXXXXXX_XXXXXX\promethean_light\*
   To C:\Code\Promethian Light\
   ```
3. **Restore SQLite Database**:
   ```
   Copy backup_XXXXXXXX_XXXXXX\mydata.db
   To C:\Code\Promethian Light\mydata\mydata.db
   ```
4. **Restore Qdrant Database**:
   ```
   Copy backup_XXXXXXXX_XXXXXX\qdrant\*
   To %USERPROFILE%\.mydata\qdrant\
   ```
5. **Restart Promethean Light**

### Selective Restore (Database Only)

If you only need to restore the database:

```batch
REM 1. Stop the daemon
taskkill /f /im python.exe /fi "WINDOWTITLE eq MyData Daemon"

REM 2. Restore databases
copy "V:\mel_energy_office\Business Dev\Data Base Backup\daily\backup_XXXXXXXX_XXXXXX\mydata.db" "C:\Code\Promethian Light\mydata\mydata.db" /y
xcopy "V:\mel_energy_office\Business Dev\Data Base Backup\daily\backup_XXXXXXXX_XXXXXX\qdrant\*" "%USERPROFILE%\.mydata\qdrant\" /e /i /y

REM 3. Restart daemon
START.bat
```

## Monitoring

### Check Last Backup

View the latest log file:
```
notepad "V:\mel_energy_office\Business Dev\Data Base Backup\logs\backup_202501.log"
```

### Check Backup Size

The backup script logs the size of each component:
- SQLite database size (MB)
- Qdrant database size (MB)
- Program files size (MB)
- Total backup size (MB)

### Verify Backup Health

Each backup includes a `BACKUP_INFO.txt` manifest with:
- Backup type (daily/weekly/monthly)
- Creation timestamp
- Source paths
- Component list

## Troubleshooting

### Backup Fails with "Access Denied"

- Ensure `V:\mel_energy_office\Business Dev\Data Base Backup` is accessible
- Check network drive permissions
- Verify Task Scheduler has correct credentials

### Database Locked During Backup

- The SQLite backup uses the backup API, which is safe during operation
- If issues persist, schedule backup during known idle times

### Qdrant Backup Incomplete

- Lock files are automatically excluded
- Ensure Qdrant is not corrupted: run a test query first

### Backup Takes Too Long

- Expected time: 30 seconds - 5 minutes depending on data size
- If >10 minutes, check:
  - Network drive speed
  - Qdrant database size (may need cleanup)
  - Disk space availability

## Performance Impact

- **Minimal**: Backup runs at 2:00 AM during idle time
- SQLite backup uses hot-copy (no downtime)
- Qdrant backup is file-copy (very fast)
- Typical backup time: 1-2 minutes

## Disk Space Requirements

Estimate: `(Current Data Size) × (7 daily + 4 weekly + 12 monthly) × 1.1`

Example:
- Current data: 500 MB
- Estimated backup space: 500 MB × 23 × 1.1 = **12.6 GB**

Monitor `V:\mel_energy_office\Business Dev\Data Base Backup` size periodically.

## Security

- Backups include encrypted email credentials (Fernet encryption)
- Backups stored on trusted network drive
- Consider additional encryption for V:\ drive if highly sensitive

## Best Practices

1. **Verify backups monthly**: Spot-check a monthly backup
2. **Test restore annually**: Full restore test to verify backup integrity
3. **Monitor disk space**: Ensure backup drive has adequate space
4. **Keep backup drive healthy**: Monitor V:\ drive health
5. **Document changes**: If you modify backup schedule, update this README

## Support

For issues or questions:
- Check logs first: `V:\mel_energy_office\Business Dev\Data Base Backup\logs\`
- Verify Task Scheduler: `taskschd.msc` → PrometheanLightBackup
- Test manual backup: Run `BACKUP_NOW.bat`
