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

$envFile = Join-Path $RootDir ".env"
if (-not (Test-Path $envFile)) {
    Write-Warning ".env not found — run .\setup.ps1 first (or the sim will run without an API key)."
}

$python = Find-Python
Write-Host "Starting Divinity Sim with: $python"
Push-Location $RootDir
try {
    & $python "main.py"
}
finally {
    Pop-Location
}
