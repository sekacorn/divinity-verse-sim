$ErrorActionPreference = "Stop"

$processes = Get-CimInstance Win32_Process |
    Where-Object {
        $_.Name -eq "python.exe" -and
        $_.CommandLine -like "*Divinity-Simulator*main.py*"
    }

if (-not $processes) {
    Write-Host "No Divinity Sim processes found."
    exit 0
}

foreach ($proc in $processes) {
    try {
        Stop-Process -Id $proc.ProcessId -Force -ErrorAction Stop
        Write-Host "Stopped process $($proc.ProcessId)"
    }
    catch {
        Write-Warning "Failed to stop process $($proc.ProcessId): $($_.Exception.Message)"
    }
}
