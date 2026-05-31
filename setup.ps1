$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir = Join-Path $RootDir ".venv"

function Find-Python {
    $candidates = @(
        (Join-Path $VenvDir "Scripts\python.exe"),
        (Join-Path $VenvDir "bin\python"),
        "C:\Users\sekac\AppData\Local\Programs\Python\Python312\python.exe",
        "C:\Users\sekac\AppData\Local\Programs\Python\Python313\python.exe",
        "C:\Users\sekac\AppData\Local\Programs\Python\Python311\python.exe"
    )
    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path $candidate)) { return $candidate }
    }
    # Avoid broken system python — skip if it can't import sys cleanly
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        $ok = & $pythonCmd.Source -c "import sys; print(sys.version)" 2>$null
        if ($LASTEXITCODE -eq 0) { return $pythonCmd.Source }
    }
    $python3Cmd = Get-Command python3 -ErrorAction SilentlyContinue
    if ($python3Cmd) {
        $ok = & $python3Cmd.Source -c "import sys" 2>$null
        if ($LASTEXITCODE -eq 0) { return $python3Cmd.Source }
    }
    throw "No working Python executable found."
}

# ── Virtual environment ──────────────────────────────────────────────────────
$basePython = Find-Python
if (-not (Test-Path $VenvDir)) {
    Write-Host "Creating virtual environment with: $basePython"
    & $basePython -m venv $VenvDir
}
$python = Join-Path $VenvDir "Scripts\python.exe"
if (-not (Test-Path $python)) { $python = Join-Path $VenvDir "bin\python" }

# ── Python dependencies ──────────────────────────────────────────────────────
Write-Host "Installing Python dependencies..."
& $python -m pip install --quiet --upgrade pip
& $python -m pip install --quiet -r (Join-Path $RootDir "requirements.txt")
& $python -m pip install --quiet -r (Join-Path $RootDir "requirements-dev.txt")

# ── Playwright browsers ──────────────────────────────────────────────────────
Write-Host "Installing Playwright browsers (chromium)..."
& $python -m playwright install chromium

# ── .env ─────────────────────────────────────────────────────────────────────
$envFile    = Join-Path $RootDir ".env"
$envExample = Join-Path $RootDir ".env.example"
if (-not (Test-Path $envFile)) {
    if (Test-Path $envExample) {
        Copy-Item $envExample $envFile
        Write-Host "Created .env from .env.example  — add your ANTHROPIC_API_KEY to enable Claude."
    } else {
        Set-Content $envFile "ANTHROPIC_API_KEY=`nSIM_MODEL=claude-haiku-4-5-20251001`nSIM_MAX_MORTALS=10`nSIM_TICK_DELAY=0"
        Write-Host "Created blank .env  — add your ANTHROPIC_API_KEY to enable Claude."
    }
}

# ── Frontend npm dependencies ────────────────────────────────────────────────
$frontendDir = Join-Path $RootDir "dashboard\frontend"
if (Test-Path (Join-Path $frontendDir "package.json")) {
    Write-Host "Installing frontend npm dependencies..."
    Push-Location $frontendDir
    try { npm install --silent }
    finally { Pop-Location }
}

Write-Host ""
Write-Host "Setup complete."
Write-Host "  Edit .env and set ANTHROPIC_API_KEY for Claude-powered mortal thoughts."
Write-Host "  Start the sim:   .\run.ps1"
Write-Host "  Run tests:       .\test.ps1"
