@echo off
echo.
echo ═══════════════════════════════════════════════════════════════════
echo  PROMETHEAN LIGHT - COMMAND REFERENCE
echo ═══════════════════════════════════════════════════════════════════
echo.
echo  QUICK ACCESS:
echo    mydata quick              Interactive menu for common queries
echo    QUICK.bat                 Same as above (double-click)
echo.
echo  SEARCH:
echo    mydata ask "query"        Search your database
echo    mydata ask "salary"       Example: search for salary info
echo.
echo  STATS:
echo    mydata stats              Database statistics
echo    mydata tags               List all tags
echo    mydata ls                 List recent documents
echo    mydata clusters           Show ML clusters
echo.
echo  SUMMARIES (Instant, 0 tokens):
echo    curl http://localhost:8000/summary/india_staff
echo    curl http://localhost:8000/summary/australia_staff
echo    curl http://localhost:8000/summary/retention_bonuses
echo.
echo  DAEMON CONTROL:
echo    START.bat                 Start the daemon
echo    KILL.bat                  Stop the daemon
echo.
echo  DATA MANAGEMENT:
echo    mydata add --stdin        Add text from clipboard
echo    echo "text" ^| mydata add --stdin
echo.
echo  HELP:
echo    mydata --help             Show all commands
echo    mydata COMMAND --help     Help for specific command
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.
pause
