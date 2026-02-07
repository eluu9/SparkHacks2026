# install.ps1 - Full environment setup for SparkHacks2026
# Usage: powershell -ExecutionPolicy Bypass -File install.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $root
Write-Host ''
Write-Host '=== SparkHacks2026 Installer ===' -ForegroundColor Cyan

# 1. Check Python is available
Write-Host ''
Write-Host '[1/5] Checking Python...' -ForegroundColor Yellow
try {
    $pyVersion = & python --version 2>&1
    Write-Host "  Found: $pyVersion" -ForegroundColor Green
} catch {
    Write-Host '  ERROR: Python not found. Install Python 3.10+ and add to PATH.' -ForegroundColor Red
    exit 1
}

# 2. Create virtual environment
Write-Host ''
Write-Host '[2/5] Creating virtual environment (.venv)...' -ForegroundColor Yellow
if (Test-Path '.venv') {
    Write-Host '  .venv already exists - recreating...' -ForegroundColor DarkYellow
    Remove-Item -Recurse -Force '.venv'
}
python -m venv .venv
Write-Host '  Created .venv' -ForegroundColor Green

# 3. Activate and install dependencies
Write-Host ''
Write-Host '[3/5] Installing dependencies...' -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt
Write-Host '  All packages installed' -ForegroundColor Green

# 4. Verify .env file
Write-Host ''
Write-Host '[4/5] Checking .env...' -ForegroundColor Yellow
if (Test-Path '.env') {
    Write-Host '  .env found' -ForegroundColor Green
} else {
    Write-Host '  WARNING: No .env file found.' -ForegroundColor Red
}

# 5. Verify critical files
Write-Host ''
Write-Host '[5/5] Verifying project files...' -ForegroundColor Yellow
$requiredFiles = @(
    'wsgi.py',
    'firebase-key.json',
    'normalization.py',
    'app/__init__.py',
    'app/extensions.py',
    'app/config.json',
    'app/models/user.py',
    'app/routes/auth.py',
    'app/routes/main.py',
    'app/routes/kit.py',
    'app/services/orchestrator.py',
    'app/services/llm_service.py',
    'app/services/planner_service.py',
    'app/services/kit_service.py',
    'app/services/query_service.py',
    'app/services/search_service.py',
    'app/services/match_service.py',
    'app/schemas/kit.schema.json',
    'app/schemas/llm_clarify_gate.schema.json',
    'app/services/prompts/clarify_gate.md',
    'app/services/prompts/kit_builder.md',
    'app/templates/base.html',
    'app/templates/index.html',
    'app/templates/login.html',
    'app/templates/signup.html',
    'app/static/js/main.js'
)

$missing = @()
foreach ($f in $requiredFiles) {
    if (-not (Test-Path $f)) {
        $missing += $f
    }
}

if ($missing.Count -eq 0) {
    Write-Host '  All project files present' -ForegroundColor Green
} else {
    Write-Host '  MISSING FILES:' -ForegroundColor Red
    foreach ($m in $missing) {
        Write-Host "    - $m" -ForegroundColor Red
    }
}

Write-Host ''
Write-Host '=== Installation Complete ===' -ForegroundColor Cyan
Write-Host 'To run the app:' -ForegroundColor White
Write-Host '  .\.venv\Scripts\Activate.ps1' -ForegroundColor Gray
Write-Host '  python wsgi.py' -ForegroundColor Gray
Write-Host ''
