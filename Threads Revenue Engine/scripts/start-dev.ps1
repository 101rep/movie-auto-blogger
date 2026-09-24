$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path .env)) { throw 'Copy .env.example to .env and set a unique ADMIN_PASSWORD first.' }
$python = Join-Path (Get-Location) '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) { throw 'Create .venv and install requirements.lock.txt first.' }
& $python -m alembic upgrade head
if ($LASTEXITCODE -ne 0) { throw 'Migration failed' }
& $python -m apps.backend.tre.seed
if ($LASTEXITCODE -ne 0) { throw 'Seed failed' }
New-Item -ItemType Directory -Force work | Out-Null
$backend = Start-Process -FilePath $python -ArgumentList '-m uvicorn apps.backend.tre.main:app --host 127.0.0.1 --port 8000' -WindowStyle Hidden -PassThru -RedirectStandardOutput work/backend.log -RedirectStandardError work/backend-error.log
$worker = Start-Process -FilePath $python -ArgumentList '-m apps.worker.main' -WindowStyle Hidden -PassThru -RedirectStandardOutput work/worker.log -RedirectStandardError work/worker-error.log
try {
    Set-Location apps/frontend
    pnpm dev
} finally {
    Stop-Process -Id $backend.Id,$worker.Id -ErrorAction SilentlyContinue
}
