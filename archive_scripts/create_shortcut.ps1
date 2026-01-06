$WshShell = New-Object -ComObject WScript.Shell
$Desktop = [Environment]::GetFolderPath('Desktop')
$Shortcut = $WshShell.CreateShortcut("$Desktop\Promethean Light.lnk")
$Shortcut.TargetPath = "C:\Code\Promethian  Light\START_PROMETHEAN_LIGHT.bat"
$Shortcut.WorkingDirectory = "C:\Code\Promethian  Light"
$Shortcut.IconLocation = "C:\Code\Promethian  Light\promethean-light-ui\src-tauri\icons\icon.ico"
$Shortcut.WindowStyle = 7
$Shortcut.Save()
Write-Host "Shortcut 'Promethean Light' created on Desktop!"
