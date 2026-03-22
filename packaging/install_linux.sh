#!/usr/bin/env bash
set -euo pipefail

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is not installed or not available in PATH." >&2
  exit 1
fi

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install .

echo
echo "LogLens installation completed."
echo "Activate later with: source .venv/bin/activate"
echo "Run with: loglens"
