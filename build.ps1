$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path

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
        $ok = & $pythonCmd.Source -c "import sys" 2>$null
        if ($LASTEXITCODE -eq 0) { return $pythonCmd.Source }
    }
    throw "No working Python executable found."
}

$python = Find-Python
$files = @(
    (Join-Path $RootDir "main.py"),
    (Join-Path $RootDir "simulation.py"),
    (Join-Path $RootDir "api\server.py"),
    (Join-Path $RootDir "api\sse.py"),
    (Join-Path $RootDir "world\clock.py"),
    (Join-Path $RootDir "world\events.py"),
    (Join-Path $RootDir "world\state.py"),
    (Join-Path $RootDir "mortals\archetypes.py"),
    (Join-Path $RootDir "mortals\memory.py"),
    (Join-Path $RootDir "mortals\agent.py"),
    (Join-Path $RootDir "deities\deity.py"),
    (Join-Path $RootDir "deities\pantheon.py"),
    (Join-Path $RootDir "divine\actions.py"),
    (Join-Path $RootDir "dashboard\cli.py")
)

Write-Host "Running Python build validation with: $python"
& $python -m py_compile @files
if ($LASTEXITCODE -ne 0) {
    Write-Error "Build validation FAILED."
    exit 1
}
Write-Host "Python build validation passed."

# TypeScript check
$frontendDir = Join-Path $RootDir "dashboard\frontend"
if (Test-Path (Join-Path $frontendDir "package.json")) {
    Write-Host "Running TypeScript type check..."
    Push-Location $frontendDir
    try {
        npx tsc --noEmit
        if ($LASTEXITCODE -ne 0) {
            Write-Error "TypeScript check FAILED."
            exit 1
        }
        Write-Host "TypeScript check passed."
    } finally {
        Pop-Location
    }
}

Write-Host "Build validation passed."
