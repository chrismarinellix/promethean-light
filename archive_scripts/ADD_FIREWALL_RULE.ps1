# Add Windows Firewall rule for Promethean Light API
# Run this as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ADDING FIREWALL RULE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    # Add inbound rule for port 8000
    New-NetFirewallRule -DisplayName "Promethean Light API" `
                        -Direction Inbound `
                        -Action Allow `
                        -Protocol TCP `
                        -LocalPort 8000 `
                        -ErrorAction Stop

    Write-Host "[SUCCESS] Firewall rule added!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Rule details:"
    Get-NetFirewallRule -DisplayName "Promethean Light API" | Format-List DisplayName, Direction, Action, Enabled

} catch {
    Write-Host "[ERROR] Failed to add firewall rule" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternative: Use netsh command" -ForegroundColor Yellow
    Write-Host 'netsh advfirewall firewall add rule name="Promethean Light API" dir=in action=allow protocol=TCP localport=8000'
}

Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
