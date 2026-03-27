#requires -Version 7.0
$ErrorActionPreference = "Stop"

function Write-Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Write-Ok($msg) { Write-Host "OK: $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "WARN: $msg" -ForegroundColor Yellow }

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $repoRoot

$envName = "valuestream-os"

Write-Step "Starting development environment (repo: $repoRoot)"

Write-Step "Precheck: conda available"
if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
  throw "Conda was not found in PATH. Install Anaconda or Miniconda and restart the terminal."
}

Write-Step "Initialize conda shell hook"
(& conda "shell.powershell" "hook") | Out-String | Invoke-Expression

Write-Step "Activate conda environment"
conda activate $envName
Write-Ok "Activated: $envName"

Write-Step "Open project in VS Code"
if (Get-Command code -ErrorAction SilentlyContinue) {
  cursor .
  Write-Ok "Cursor opened"
} else {
  Write-Warn "Cursor not found in PATH"
}

Write-Step "Development environment ready 🚀"
