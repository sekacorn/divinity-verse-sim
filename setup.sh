#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"

find_python() {
  if [[ -x "$VENV_DIR/Scripts/python.exe" ]]; then
    printf '%s\n' "$VENV_DIR/Scripts/python.exe"
    return 0
  fi
  if [[ -x "$VENV_DIR/bin/python" ]]; then
    printf '%s\n' "$VENV_DIR/bin/python"
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
  if [[ -x "/c/Users/sekac/AppData/Local/Programs/Python/Python313/python.exe" ]]; then
    printf '%s\n' "/c/Users/sekac/AppData/Local/Programs/Python/Python313/python.exe"
    return 0
  fi
  return 1
}

if [[ ! -d "$VENV_DIR" ]]; then
  BASE_PYTHON="$(find_python)"
  echo "Creating virtual environment with: $BASE_PYTHON"
  "$BASE_PYTHON" -m venv "$VENV_DIR"
fi

PYTHON="$(find_python)"
echo "Using Python: $PYTHON"
"$PYTHON" -m pip install -r "$ROOT_DIR/requirements.txt"

if [[ ! -f "$ROOT_DIR/.env" ]]; then
  cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
  echo "Created .env from .env.example"
fi

echo "Setup complete."
