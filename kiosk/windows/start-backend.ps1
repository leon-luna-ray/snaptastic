<#
.SYNOPSIS
  Runs the Snaptastic backend in this console, with logs on screen. Ctrl+C stops it.

  powershell -ExecutionPolicy Bypass -File kiosk\windows\start-backend.ps1 [-Camera webcam|fuji] [-WebcamIndex 0]

  Works both from the repo and from the install folder (C:\Snaptastic\kiosk).
  Stop the scheduled task first if it's running, or the port will be taken:
    Stop-ScheduledTask -TaskName 'Snaptastic Backend'
#>
param(
    [ValidateSet('webcam', 'fuji')]
    [string]$Camera,
    [int]$WebcamIndex = -1
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
# From the repo, kiosk\windows is two levels down; from the install it's one.
if (-not (Test-Path (Join-Path $root 'backend'))) { $root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path }
$backend = Join-Path $root 'backend'
$python = Join-Path $backend '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    throw "No virtual environment at $backend\.venv. Create one with: py -3.12 -m venv backend\.venv; backend\.venv\Scripts\pip install -r backend\requirements.txt"
}

if ($Camera) { $env:SNAPTASTIC_CAMERA = $Camera }
if ($WebcamIndex -ge 0) { $env:SNAPTASTIC_WEBCAM_INDEX = "$WebcamIndex" }

Push-Location $backend
try {
    & $python run.py
} finally {
    Pop-Location
}
