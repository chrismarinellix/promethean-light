# PowerShell launcher for Prometheus Light - God Mode

# Set console colors for retro feel
$Host.UI.RawUI.BackgroundColor = "Black"
$Host.UI.RawUI.ForegroundColor = "Green"
Clear-Host

# Banner
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                                      ║" -ForegroundColor Cyan
Write-Host "║    ██████╗ ██████╗  ██████╗ ███╗   ███╗███████╗████████╗██╗  ██╗   ║" -ForegroundColor Cyan
Write-Host "║    ██╔══██╗██╔══██╗██╔═══██╗████╗ ████║██╔════╝╚══██╔══╝██║  ██║   ║" -ForegroundColor Cyan
Write-Host "║    ██████╔╝██████╔╝██║   ██║██╔████╔██║█████╗     ██║   ███████║   ║" -ForegroundColor Cyan
Write-Host "║    ██╔═══╝ ██╔══██╗██║   ██║██║╚██╔╝██║██╔══╝     ██║   ██╔══██║   ║" -ForegroundColor Cyan
Write-Host "║    ██║     ██║  ██║╚██████╔╝██║ ╚═╝ ██║███████╗   ██║   ██║  ██║   ║" -ForegroundColor Cyan
Write-Host "║    ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝   ║" -ForegroundColor Cyan
Write-Host "║                                                                      ║" -ForegroundColor Cyan
Write-Host "║             ██╗     ██╗ ██████╗ ██╗  ██╗████████╗                   ║" -ForegroundColor Green
Write-Host "║             ██║     ██║██╔════╝ ██║  ██║╚══██╔══╝                   ║" -ForegroundColor Green
Write-Host "║             ██║     ██║██║  ███╗███████║   ██║                      ║" -ForegroundColor Green
Write-Host "║             ██║     ██║██║   ██║██╔══██║   ██║                      ║" -ForegroundColor Green
Write-Host "║             ███████╗██║╚██████╔╝██║  ██║   ██║                      ║" -ForegroundColor Green
Write-Host "║             ╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝                      ║" -ForegroundColor Green
Write-Host "║                                                                      ║" -ForegroundColor Cyan
Write-Host "║                        ══ GOD MODE ══                                ║" -ForegroundColor Yellow
Write-Host "║                                                                      ║" -ForegroundColor Cyan
Write-Host "║         Encrypted · Local · ML-Powered Knowledge Base               ║" -ForegroundColor White
Write-Host "║                                                                      ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "Initializing..." -ForegroundColor Yellow
Start-Sleep -Milliseconds 500

# Check if initialized
if (-not (Test-Path "$env:USERPROFILE\.mydata\master.key")) {
    Write-Host ""
    Write-Host "⚠ First time setup required" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Running setup..." -ForegroundColor Cyan
    mydata setup
}

Write-Host ""
Write-Host "Ready. Type 'mydata --help' for commands" -ForegroundColor Green
Write-Host ""

# Start interactive session
if ($args.Length -eq 0) {
    Write-Host "Quick commands:" -ForegroundColor Cyan
    Write-Host "  mydata daemon          - Start background services" -ForegroundColor White
    Write-Host "  mydata ask 'query'     - Search your knowledge base" -ForegroundColor White
    Write-Host "  mydata ls              - List documents" -ForegroundColor White
    Write-Host "  mydata stats           - Show statistics" -ForegroundColor White
    Write-Host ""
} else {
    # Run command
    mydata @args
}
