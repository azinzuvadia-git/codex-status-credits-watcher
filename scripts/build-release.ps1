param(
  [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

& $Python -m pip install --upgrade pip
& $Python -m pip install -r requirements-build.txt
& $Python -m PyInstaller --noconfirm --onefile --windowed --name codex-credits-watcher-onefile --add-data "VERSION;." app\main.py
& $Python -m PyInstaller --noconfirm --onedir --windowed --name codex-credits-watcher-onedir --add-data "VERSION;." app\main.py
& pwsh scripts\generate-checksums.ps1
Write-Output "Build complete: dist/codex-credits-watcher-onefile.exe and dist/codex-credits-watcher-onedir/"
