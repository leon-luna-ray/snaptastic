<#
.SYNOPSIS
  Opens the booth in Edge's full-screen kiosk mode, without locking the PC down.
  Close it with Alt+F4.

  powershell -ExecutionPolicy Bypass -File kiosk\windows\launch-kiosk-dev.ps1 [-Url http://localhost:5173]
#>
param(
    [string]$Url = 'http://localhost:8080'
)

$edge = @(
    "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
    "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $edge) { throw 'Microsoft Edge not found.' }

# A separate profile, so kiosk mode applies even while normal Edge windows are open.
$profileDir = Join-Path $env:TEMP 'snaptastic-kiosk-edge'
Start-Process $edge -ArgumentList @(
    "--kiosk", $Url,
    "--edge-kiosk-type=fullscreen",
    "--no-first-run",
    "--user-data-dir=$profileDir"
)
