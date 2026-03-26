#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STOPPED=0

if command -v powershell.exe >/dev/null 2>&1; then
  POWERSHELL_ROOT="${ROOT_DIR//\\/\\\\}"
  powershell.exe -NoProfile -Command "
    \$root = '$POWERSHELL_ROOT';
    \$processes = Get-CimInstance Win32_Process |
      Where-Object {
        \$_.Name -eq 'python.exe' -and
        \$_.CommandLine -like '*Divinity-Simulator*main.py*'
      };
    foreach (\$proc in \$processes) {
      try { Stop-Process -Id \$proc.ProcessId -Force -ErrorAction Stop } catch {}
    }
  " >/dev/null
  STOPPED=1
elif command -v pkill >/dev/null 2>&1; then
  pkill -f "Divinity-Simulator.*main.py" || true
  STOPPED=1
fi

if [[ "$STOPPED" -eq 1 ]]; then
  echo "Stopped Divinity Sim processes."
else
  echo "No supported process killer found."
fi
