@echo off
cd /d "C:\Code\Promethian  Light"

echo.
echo ============================================================
echo GRITLM-7B DATABASE REBUILD
echo ============================================================
echo.
echo FIXES:
echo   ✓ Dimension mismatch (768 -^> 4096)
echo   ✓ Missing Chunk import in daemon
echo   ✓ Migration script bugs fixed
echo.
echo This will rebuild your Qdrant vector database with 4096-dim
echo embeddings for GritLM-7B.
echo.
echo Time estimate: ~15-30 minutes for 3500 documents
echo.
pause

python migrate_to_gritlm.py

pause
