$ErrorActionPreference = "Stop"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python is not installed or not available in PATH."
}

python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install .

Write-Host ""
Write-Host "LogLens installation completed."
Write-Host "Activate later with: .\.venv\Scripts\Activate.ps1"
Write-Host "Run with: loglens"
