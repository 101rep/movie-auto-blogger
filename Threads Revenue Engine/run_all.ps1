$ErrorActionPreference = 'Continue'
$engineDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $engineDir) {
    $engineDir = (Get-Location).Path
}
Set-Location -LiteralPath $engineDir

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Threads Revenue Engine V3 (AI Content Commerce OS)     " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# Clean up any lingering process on port 8000 to guarantee latest code & templates
try {
    $existing = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
    if ($existing) {
        Write-Host "      Refreshing previous server instance on port 8000..." -ForegroundColor DarkGray
        $existing | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
        Start-Sleep -Milliseconds 600
    }
} catch {}

# 1. Start FastAPI Backend with Full AI Web Dashboard
Write-Host "[1/2] AI Content Commerce OS Backend Server Starting..." -ForegroundColor Green
Start-Process python -ArgumentList "-m", "uvicorn", "apps.backend.tre.main:app", "--host", "127.0.0.1", "--port", "8000" -WorkingDirectory $engineDir

$serverOnline = $false
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Milliseconds 500
    try {
        $res = Invoke-WebRequest -Uri "http://127.0.0.1:8000/" -UseBasicParsing -TimeoutSec 2
        if ($res.StatusCode -eq 200) { 
            Write-Host "      Web Dashboard Online (http://localhost:8000/)" -ForegroundColor Gray
            $serverOnline = $true
            break 
        }
    } catch {}
}

# 2. Start Background Worker
Write-Host "[2/2] Background Worker Starting..." -ForegroundColor Green
Start-Process python -ArgumentList "-m", "apps.worker.main" -WorkingDirectory $engineDir
Write-Host "      Worker Active (Auto-scheduler / Queue polling)" -ForegroundColor Gray

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   [SUCCESS] Engine Online! Opening Dashboard...         " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

Start-Sleep -Seconds 1
# Open the visual AI Content Commerce OS Web Dashboard
Start-Process "http://localhost:8000/"

Write-Host ""
Write-Host "Engine running in background. You can close this launcher anytime." -ForegroundColor DarkGray
try {
    if ([Environment]::UserInteractive -and -not [Console]::IsInputRedirected) {
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
} catch {}
