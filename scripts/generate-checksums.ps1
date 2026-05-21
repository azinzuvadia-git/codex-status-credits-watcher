param(
  [string]$OneFilePath = "dist/codex-credits-watcher-onefile.exe",
  [string]$OneDirExePath = "dist/codex-credits-watcher-onedir/codex-credits-watcher-onedir.exe"
)

if (-not (Test-Path -LiteralPath $OneFilePath)) {
  Write-Error "Onefile EXE not found: $OneFilePath"
  exit 1
}

if (-not (Test-Path -LiteralPath $OneDirExePath)) {
  Write-Error "Onedir EXE not found: $OneDirExePath"
  exit 1
}

$oneHash = (Get-FileHash -LiteralPath $OneFilePath -Algorithm SHA256).Hash.ToLower()
$dirHash = (Get-FileHash -LiteralPath $OneDirExePath -Algorithm SHA256).Hash.ToLower()
$outPath = "dist/SHA256SUMS.txt"
"$oneHash  $(Split-Path -Leaf $OneFilePath)" | Set-Content -Encoding ascii $outPath
"$dirHash  $(Split-Path -Leaf $OneDirExePath)" | Add-Content -Encoding ascii $outPath
Write-Output "Wrote: $outPath"
