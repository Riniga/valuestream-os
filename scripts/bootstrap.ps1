#requires -Version 7.0
$ErrorActionPreference = "Stop"

function Write-Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "OK: $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "WARN: $msg" -ForegroundColor Yellow }

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $repoRoot

$envName = "valuestream-os"
$envFile = Join-Path $repoRoot "environment.yml"

Write-Step "Bootstrap ValueStream OS (repo: $repoRoot)"

Write-Step "Precheck: conda available"
if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
  throw "Conda was not found in PATH. Install Anaconda or Miniconda and restart the terminal."
}

if (-not (Test-Path $envFile)) {
  throw "Could not find environment.yml in the repository root."
}

Write-Step "Initialize conda shell hook"
(& conda "shell.powershell" "hook") | Out-String | Invoke-Expression

Write-Step "Create or update conda environment: $envName"
$existing = conda env list | Select-String -Pattern "^\s*$([regex]::Escape($envName))\s+"
if ($existing) {
  Write-Warn "Conda environment '$envName' already exists. Running update."
  conda env update -n $envName -f $envFile
} else {
  conda env create -n $envName -f $envFile
}
Write-Ok "Conda environment is ready"

Write-Step "Activate conda environment"
conda activate $envName
Write-Ok "Activated: $envName"

Write-Step "Create .env if missing"
$envExample = Join-Path $repoRoot "setup/environment/.env.example"
$envTarget  = Join-Path $repoRoot ".env"

if (-not (Test-Path $envTarget)) {
  if (Test-Path $envExample) {
    Copy-Item $envExample $envTarget
    Write-Ok ".env created from .env.example"
  } else {
    Write-Warn "No .env.example found. Skipping .env creation."
  }
} else {
  Write-Ok ".env already exists"
}

Write-Step "Bootstrap complete ✅"