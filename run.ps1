$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path

function Find-Python {
    $candidates = @(
        (Join-Path $RootDir ".venv\Scripts\python.exe"),
        (Join-Path $RootDir ".venv\bin\python"),
        "C:\Users\sekac\AppData\Local\Programs\Python\Python313\python.exe"
    )

    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path $candidate)) {
            return $candidate
        }
    }

    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) { return $pythonCmd.Source }

    $python3Cmd = Get-Command python3 -ErrorAction SilentlyContinue
    if ($python3Cmd) { return $python3Cmd.Source }

    throw "Python executable not found."
}

$envFile = Join-Path $RootDir ".env"
if (-not (Test-Path $envFile)) {
    throw "Missing .env. Run .\setup.ps1 first."
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
