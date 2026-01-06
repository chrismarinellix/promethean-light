$startup = [Environment]::GetFolderPath('Startup')
$shortcut = Join-Path $startup 'Promethean Light.lnk'
$shell = New-Object -ComObject WScript.Shell
$lnk = $shell.CreateShortcut($shortcut)
$lnk.TargetPath = 'C:\Code\Promethian  Light\START_DAEMON_SILENT.bat'
$lnk.WorkingDirectory = 'C:\Code\Promethian  Light'
$lnk.WindowStyle = 7
$lnk.Save()
Write-Host "Shortcut created at: $shortcut"
