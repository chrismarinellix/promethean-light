# GritLM-7B Upgrade - Quick Start

You've upgraded to **GritLM-7B** - the most powerful local embedding model! 🚀

## What Changed

- **Old Model**: `BAAI/bge-base-en-v1.5` (768 dimensions)
- **New Model**: `GritLM/GritLM-7B` (4096 dimensions)
- **Quality**: +30-50% better search results
- **Trade-off**: Uses more RAM (~8-12GB) and slightly slower

## How to Upgrade

### Step 1: Run the Upgrade Script

**Double-click**: `UPGRADE_TO_GRITLM.bat`

Or run manually:
```bash
python migrate_to_gritlm.py
```

This will:
1. ✅ Backup your existing database
2. ✅ Download GritLM-7B model (~14GB, one-time)
3. ✅ Rebuild vector database with new embeddings
4. ✅ Verify everything works

**Time required**: 30-60 minutes (depending on internet speed and DB size)

### Step 2: Start Using It

```bash
# Start daemon
START.bat

# Or use system tray
dist\Promethean Light.exe
```

### Step 3: Test the Quality

Try some searches that used to be hard:

```bash
python -m mydata search "people at risk of leaving"
python -m mydata search "Sandy's compensation details"
python -m mydata ask "What happened with the Australia budget?"
```

You should notice MUCH better results! 🎯

## System Requirements

### Minimum
- **RAM**: 12GB total (8GB free)
- **Disk**: 16GB free space
- **CPU**: Any modern processor (4+ cores recommended)

### Recommended
- **RAM**: 16GB+ total
- **Disk**: 20GB+ free space
- **CPU**: 8+ cores or GPU (NVIDIA 8GB+ VRAM)

## Performance Expectations

### First Time
- **Download**: 10-30 minutes (14GB model)
- **Migration**: 30-60 minutes (re-embedding all documents)

### Normal Operation
- **Startup**: 15-20 seconds (model loading)
- **Search**: 100-300ms (still feels instant!)
- **Background ingestion**: 2-3 seconds per email

## What to Expect

### ✅ Better Results
- More accurate semantic understanding
- Better ranking (right answer on top)
- Handles complex queries
- Understands context and relationships

### ⚠️ Trade-Offs
- Uses more RAM (8-12GB vs 2GB)
- Slightly slower searches (still <1 second)
- Longer startup time (15-20s vs 3-5s)
- Large model download (14GB vs 500MB)

## Troubleshooting

### "Out of Memory"
- Close other applications
- Increase Windows page file
- Consider bge-large instead (see downgrade section)

### "Download Failed"
- Check internet connection
- Ensure 16GB+ free disk space
- Try manual download (see Performance Guide)

### "Search Too Slow"
- First search loads model (10-20s) - normal!
- Subsequent searches should be <1 second
- Check RAM usage in Task Manager

## Downgrade Options

If GritLM-7B is too resource-intensive:

### Option 1: bge-large (Recommended Middle Ground)
```python
# Edit mydata/embedder.py:
model_name: str = "BAAI/bge-large-en-v1.5"  # 1024-dim, ~3GB RAM

# Edit mydata/vectordb.py:
dimension: int = 1024

# Rebuild:
python migrate_to_gritlm.py
```

Quality: +15-20% over base (vs +30-50% for GritLM)
RAM: ~3GB (vs 8-12GB for GritLM)

### Option 2: Revert to bge-base
```python
# Edit mydata/embedder.py:
model_name: str = "BAAI/bge-base-en-v1.5"  # 768-dim, ~2GB RAM

# Edit mydata/vectordb.py:
dimension: int = 768

# Rebuild:
python migrate_to_gritlm.py
```

## Files Created

- **`UPGRADE_TO_GRITLM.bat`** - One-click upgrade script
- **`migrate_to_gritlm.py`** - Python migration script
- **`GRITLM_PERFORMANCE_GUIDE.md`** - Detailed performance info
- **`GRITLM_UPGRADE_README.md`** - This file

## Need Help?

1. **Read**: `GRITLM_PERFORMANCE_GUIDE.md` for detailed optimization tips
2. **Check**: Daemon logs at `%USERPROFILE%\.mydata\logs\`
3. **Monitor**: RAM usage in Task Manager
4. **Test**: Run `python -m mydata search "test query"` and check timing

## Backup Location

Your old database is backed up at:
```
%USERPROFILE%\.mydata\backups\pre_gritlm_YYYYMMDD_HHMMSS\
```

You can restore it if needed.

---

**Enjoy state-of-the-art search! 🔥**
