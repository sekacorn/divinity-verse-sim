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

Write-Host "Running build validation with: $python"
& $python -m py_compile @files
Write-Host "Build validation passed."
