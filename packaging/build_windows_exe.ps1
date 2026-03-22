$ErrorActionPreference = "Stop"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python is not installed or not available in PATH."
}

New-Item -ItemType Directory -Force .\packaging\build | Out-Null
New-Item -ItemType Directory -Force .\packaging\dist | Out-Null
New-Item -ItemType Directory -Force .\packaging\temp\pyinstaller | Out-Null

$env:TMP = (Resolve-Path .\packaging\temp\pyinstaller).Path
$env:TEMP = $env:TMP

python -m pip install --upgrade pyinstaller
python -m PyInstaller --clean --onefile --name loglens --specpath packaging --distpath packaging/dist --workpath packaging/build main.py

Write-Host ""
Write-Host "Build completed."
Write-Host "Executable: .\packaging\dist\loglens.exe"
