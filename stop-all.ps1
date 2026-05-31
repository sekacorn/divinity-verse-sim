$ErrorActionPreference = "Continue"

# ── Stop Python backend ───────────────────────────────────────────────────────
$backendProcs = Get-CimInstance Win32_Process |
    Where-Object {
        $_.Name -eq "python.exe" -and (
            $_.CommandLine -like "*start_server.py*" -or
            $_.CommandLine -like "*divinity*main.py*" -or
            $_.CommandLine -like "*\main.py*"
        )
    }

if ($backendProcs) {
    foreach ($proc in $backendProcs) {
        try {
            Stop-Process -Id $proc.ProcessId -Force -ErrorAction Stop
            Write-Host "Stopped Python backend PID $($proc.ProcessId)"
        } catch {
            Write-Warning "Could not stop PID $($proc.ProcessId): $($_.Exception.Message)"
        }
    }
} else {
    Write-Host "No Divinity Sim Python backend found running."
}

# ── Stop Vite / Node frontend ─────────────────────────────────────────────────
$frontendProcs = Get-CimInstance Win32_Process |
    Where-Object {
        $_.Name -in @("node.exe", "node") -and (
            $_.CommandLine -like "*vite*" -or
            $_.CommandLine -like "*divinity*frontend*"
        )
    }

if ($frontendProcs) {
    foreach ($proc in $frontendProcs) {
        try {
            Stop-Process -Id $proc.ProcessId -Force -ErrorAction Stop
            Write-Host "Stopped Vite/Node PID $($proc.ProcessId)"
        } catch {
            Write-Warning "Could not stop PID $($proc.ProcessId): $($_.Exception.Message)"
        }
    }
} else {
    Write-Host "No Vite/Node frontend found running."
}

Write-Host "Done."
