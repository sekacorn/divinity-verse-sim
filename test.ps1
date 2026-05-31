###############################################################################
# test.ps1 — Run all tests (API + E2E) for the Divinity Verse Sim
#
# Usage:
#   .\test.ps1              # all tests (API + E2E, headless)
#   .\test.ps1 -ApiOnly     # API tests only (no browser, no servers needed)
#   .\test.ps1 -Headed      # E2E tests with visible browser
###############################################################################
param(
    [switch]$ApiOnly,
    [switch]$Headed
)

$ErrorActionPreference = "Stop"
$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# ── Find Python ───────────────────────────────────────────────────────────────
function Find-Python {
    $candidates = @(
        (Join-Path $RootDir ".venv\Scripts\python.exe"),
        (Join-Path $RootDir ".venv\bin\python"),
        "C:\Users\sekac\AppData\Local\Programs\Python\Python312\python.exe",
        "C:\Users\sekac\AppData\Local\Programs\Python\Python313\python.exe",
        "C:\Users\sekac\AppData\Local\Programs\Python\Python311\python.exe"
    )
    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path $candidate)) { return $candidate }
    }
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        & $pythonCmd.Source -c "import sys" 2>$null
        if ($LASTEXITCODE -eq 0) { return $pythonCmd.Source }
    }
    throw "No working Python executable found."
}

$python = Find-Python
Write-Host "Using Python: $python"

# ── Helper: wait for a TCP port to be open ────────────────────────────────────
function Wait-Port {
    param([int]$Port, [int]$TimeoutSec = 20, [string]$Name = "service")
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    Write-Host -NoNewline "Waiting for $Name on :$Port "
    while ((Get-Date) -lt $deadline) {
        try {
            $tcp = New-Object System.Net.Sockets.TcpClient
            $tcp.Connect("127.0.0.1", $Port)
            $tcp.Close()
            Write-Host " ready."
            return $true
        } catch { }
        Write-Host -NoNewline "."
        Start-Sleep -Milliseconds 500
    }
    Write-Host " TIMEOUT."
    return $false
}

$backendJob  = $null
$frontendJob = $null
$exitCode    = 0

try {
    # ── API-only tests (no servers needed, uses TestClient) ───────────────────
    Write-Host ""
    Write-Host "━━━ API Tests (no live server) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    Push-Location $RootDir
    & $python -m pytest tests/test_api.py -v --tb=short -m "not e2e"
    $apiExit = $LASTEXITCODE
    Pop-Location

    if ($apiExit -ne 0) {
        Write-Error "API tests FAILED (exit $apiExit)."
        $exitCode = $apiExit
    } else {
        Write-Host "API tests PASSED."
    }

    if ($ApiOnly) {
        Write-Host "Skipping E2E tests (-ApiOnly flag set)."
        exit $exitCode
    }

    # ── Start backend (port 8000) ─────────────────────────────────────────────
    Write-Host ""
    Write-Host "━━━ Starting backend (port 8000) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    $backendJob = Start-Job -ScriptBlock {
        param($rootDir, $py)
        Set-Location $rootDir
        & $py "start_server.py" 2>&1
    } -ArgumentList $RootDir, $python

    if (-not (Wait-Port -Port 8000 -TimeoutSec 25 -Name "backend")) {
        throw "Backend failed to start on port 8000."
    }

    # ── Start frontend (port 5173) ────────────────────────────────────────────
    Write-Host ""
    Write-Host "━━━ Starting frontend dev server (port 5173) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    $frontendDir = Join-Path $RootDir "dashboard\frontend"
    $frontendJob = Start-Job -ScriptBlock {
        param($dir)
        Set-Location $dir
        npm run dev -- --port 5173 2>&1
    } -ArgumentList $frontendDir

    if (-not (Wait-Port -Port 5173 -TimeoutSec 20 -Name "frontend")) {
        throw "Frontend failed to start on port 5173."
    }

    # ── E2E tests ─────────────────────────────────────────────────────────────
    Write-Host ""
    Write-Host "━━━ E2E Tests (Playwright) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    # Use installed system Chrome via channel (avoids 182 MB Chromium download)
    $e2eArgs = @("tests/test_e2e.py", "-v", "--tb=short")
    if ($Headed) { $e2eArgs += "--headed" }

    Push-Location $RootDir
    & $python -m pytest @e2eArgs
    $e2eExit = $LASTEXITCODE
    Pop-Location

    if ($e2eExit -ne 0) {
        Write-Error "E2E tests FAILED (exit $e2eExit)."
        $exitCode = $e2eExit
    } else {
        Write-Host "E2E tests PASSED."
    }

} finally {
    # ── Teardown ──────────────────────────────────────────────────────────────
    Write-Host ""
    Write-Host "━━━ Teardown ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    foreach ($job in @($backendJob, $frontendJob)) {
        if ($job) {
            Stop-Job  $job -ErrorAction SilentlyContinue
            Remove-Job $job -ErrorAction SilentlyContinue
        }
    }

    # Also kill any orphaned processes
    Get-CimInstance Win32_Process |
        Where-Object {
            ($_.Name -eq "python.exe" -and (
                $_.CommandLine -like "*start_server.py*" -or
                $_.CommandLine -like "*divinity*main.py*" -or
                $_.CommandLine -like "*\main.py*"
            )) -or
            ($_.Name -eq "node.exe"   -and $_.CommandLine -like "*vite*")
        } |
        ForEach-Object {
            try { Stop-Process -Id $_.ProcessId -Force -ErrorAction Stop }
            catch { }
        }

    Write-Host "Servers stopped."
}

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "ALL TESTS PASSED." -ForegroundColor Green
} else {
    Write-Host "SOME TESTS FAILED." -ForegroundColor Red
}
exit $exitCode
