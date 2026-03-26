#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

find_python() {
  if [[ -x "$ROOT_DIR/.venv/Scripts/python.exe" ]]; then
    printf '%s\n' "$ROOT_DIR/.venv/Scripts/python.exe"
    return 0
  fi
  if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
    printf '%s\n' "$ROOT_DIR/.venv/bin/python"
    return 0
  fi
  if command -v python >/dev/null 2>&1; then
    command -v python
    return 0
  fi
  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return 0
  fi
  return 1
}

PYTHON="$(find_python)"

echo "Running build validation with: $PYTHON"
"$PYTHON" -m py_compile \
  "$ROOT_DIR/main.py" \
  "$ROOT_DIR/simulation.py" \
  "$ROOT_DIR/api/server.py" \
  "$ROOT_DIR/api/sse.py" \
  "$ROOT_DIR/world/clock.py" \
  "$ROOT_DIR/world/events.py" \
  "$ROOT_DIR/world/state.py" \
  "$ROOT_DIR/mortals/archetypes.py" \
  "$ROOT_DIR/mortals/memory.py" \
  "$ROOT_DIR/mortals/agent.py" \
  "$ROOT_DIR/deities/deity.py" \
  "$ROOT_DIR/deities/pantheon.py" \
  "$ROOT_DIR/divine/actions.py" \
  "$ROOT_DIR/dashboard/cli.py"

echo "Build validation passed."
