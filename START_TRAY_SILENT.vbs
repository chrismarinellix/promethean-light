Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Code\Promethian  Light"

' Set environment variables
WshShell.Environment("Process")("API_HOST") = "127.0.0.1"
WshShell.Environment("Process")("API_PORT") = "8000"
WshShell.Environment("Process")("MYDATA_PASSPHRASE") = "prom"

' Start daemon minimized
WshShell.Run "cmd /c python -m mydata daemon", 7, False

' Wait for daemon to start
WScript.Sleep 3000

' Start system tray (no window)
WshShell.Run "pythonw archive_scripts\system_tray.py", 0, False
