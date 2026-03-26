$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir = Join-Path $RootDir ".venv"

function Find-Python {
    $candidates = @(
        (Join-Path $VenvDir "Scripts\python.exe"),
        (Join-Path $VenvDir "bin\python"),
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

if (-not (Test-Path $VenvDir)) {
    $basePython = Find-Python
    Write-Host "Creating virtual environment with: $basePython"
    & $basePython -m venv $VenvDir
}

$python = Find-Python
Write-Host "Using Python: $python"
& $python -m pip install -r (Join-Path $RootDir "requirements.txt")

$envFile = Join-Path $RootDir ".env"
$envExample = Join-Path $RootDir ".env.example"
if (-not (Test-Path $envFile) -and (Test-Path $envExample)) {
    Copy-Item $envExample $envFile
    Write-Host "Created .env from .env.example"
}

Write-Host "Setup complete."
