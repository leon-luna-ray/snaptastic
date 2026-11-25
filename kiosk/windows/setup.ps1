<#
.SYNOPSIS
  Builds Snaptastic and installs it as a Windows kiosk backend.

.DESCRIPTION
  Run from an elevated (Run as administrator) PowerShell, from anywhere:

    powershell -ExecutionPolicy Bypass -File kiosk\windows\setup.ps1 -KioskUser Kiosk

  Re-run it after pulling changes to update the install. It:
    1. Builds the frontend (frontend\dist).
    2. Copies the app to -InstallDir (default C:\Snaptastic). The kiosk account
       can't read files inside another user's profile, so it can't run from here.
    3. Creates a Python virtual environment there and installs the requirements.
    4. Sets the camera choice as machine environment variables.
    5. Registers the "Snaptastic Backend" scheduled task, which starts the
       backend hidden (pythonw) when -KioskUser signs in and restarts it if it dies.

  Leave out -KioskUser to register the task for your own account, which is handy
  for testing before the kiosk account exists. Run it again with -KioskUser later.

.PARAMETER InstallPrereqs
  Install Python 3.12 and Node.js LTS with winget first if they're missing.
#>
[CmdletBinding()]
param(
    [string]$KioskUser,
    [string]$InstallDir = 'C:\Snaptastic',
    [ValidateSet('webcam', 'fuji')]
    [string]$Camera = 'webcam',
    [int]$WebcamIndex = 0,
    [switch]$InstallPrereqs
)

$ErrorActionPreference = 'Stop'
$TaskName = 'Snaptastic Backend'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path

function Write-Step($text) { Write-Host "`n==> $text" -ForegroundColor Cyan }

function Update-SessionPath {
    $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' +
                [Environment]::GetEnvironmentVariable('Path', 'User')
}

function Find-Python {
    # Probing missing versions writes to stderr; under 'Stop' that would abort the script.
    $ErrorActionPreference = 'Continue'
    # The pinned requirements have wheels for Python 3.10-3.13.
    if (Get-Command py -ErrorAction SilentlyContinue) {
        foreach ($v in '3.12', '3.13', '3.11', '3.10') {
            $exe = & py "-$v" -c 'import sys; print(sys.executable)' 2>$null
            if ($LASTEXITCODE -eq 0 -and $exe) { return $exe.Trim() }
        }
    }
    $python = Get-Command python -ErrorAction SilentlyContinue
    # Skip the Microsoft Store stub in WindowsApps, which only opens the Store.
    if ($python -and $python.Source -notlike '*WindowsApps*') {
        $ok = & $python.Source -c 'import sys; print(int((3,10) <= sys.version_info[:2] <= (3,13)))' 2>$null
        if ($ok -eq '1') { return $python.Source }
    }
    return $null
}

function Invoke-Native {
    param([string]$Exe, [string[]]$Arguments)
    & $Exe @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Exe $($Arguments -join ' ') failed (exit code $LASTEXITCODE)" }
}

# --- 0. Checks --------------------------------------------------------------
$identity = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
if (-not $identity.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Run this from an elevated PowerShell (right-click > Run as administrator).'
}
if (-not $KioskUser) { $KioskUser = $env:USERNAME }
if (-not (Get-LocalUser -Name $KioskUser -ErrorAction SilentlyContinue)) {
    throw "There's no local account named '$KioskUser'. Create the kiosk account first (see kiosk\windows\README.md), or leave out -KioskUser."
}

# --- 1. Prerequisites ---------------------------------------------------------
Write-Step 'Checking for Python and Node.js'
if ($InstallPrereqs) {
    if (-not (Find-Python)) {
        winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements
    }
    if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
        winget install --id OpenJS.NodeJS.LTS -e --accept-source-agreements --accept-package-agreements
    }
    Update-SessionPath
}
$Python = Find-Python
if (-not $Python) { throw 'Python 3.10-3.13 not found. Re-run with -InstallPrereqs, or: winget install Python.Python.3.12' }
if (-not (Get-Command npx -ErrorAction SilentlyContinue)) { throw 'Node.js not found. Re-run with -InstallPrereqs, or: winget install OpenJS.NodeJS.LTS' }
Write-Host "Python: $Python"
Write-Host "Node:   $(node --version)"

# --- 2. Build the frontend ----------------------------------------------------
Write-Step 'Building the booth UI'
Push-Location (Join-Path $RepoRoot 'frontend')
try {
    Invoke-Native npx @('--yes', 'pnpm@9', 'install', '--frozen-lockfile')
    Invoke-Native npx @('--yes', 'pnpm@9', 'run', 'build')
} finally {
    Pop-Location
}

# --- 3. Copy the app to the install folder --------------------------------------
Write-Step "Installing to $InstallDir"
$backendDest = Join-Path $InstallDir 'backend'
# /MIR mirrors the code; /XD keeps the venv, photos and logs that live only in the install.
robocopy (Join-Path $RepoRoot 'backend') $backendDest /MIR /NFL /NDL /NJH /NP `
    /XD .venv venv photos logs __pycache__ /XF '*.pyc' | Out-Null
if ($LASTEXITCODE -ge 8) { throw "Copying the backend failed (robocopy exit code $LASTEXITCODE)" }
robocopy (Join-Path $RepoRoot 'frontend\dist') (Join-Path $InstallDir 'frontend\dist') /MIR /NFL /NDL /NJH /NP | Out-Null
if ($LASTEXITCODE -ge 8) { throw "Copying the frontend failed (robocopy exit code $LASTEXITCODE)" }
robocopy $PSScriptRoot (Join-Path $InstallDir 'kiosk') /MIR /NFL /NDL /NJH /NP | Out-Null
if ($LASTEXITCODE -ge 8) { throw "Copying the kiosk scripts failed (robocopy exit code $LASTEXITCODE)" }
$global:LASTEXITCODE = 0

foreach ($dir in 'photos', 'logs') {
    $path = Join-Path $backendDest $dir
    New-Item -ItemType Directory -Force $path | Out-Null
    # The backend runs as the kiosk account, which must be able to write here.
    Invoke-Native icacls @($path, '/grant', "${KioskUser}:(OI)(CI)M", '/Q')
}

# --- 4. Python environment ------------------------------------------------------
Write-Step 'Installing Python packages'
$venv = Join-Path $backendDest '.venv'
if (-not (Test-Path (Join-Path $venv 'Scripts\python.exe'))) {
    Invoke-Native $Python @('-m', 'venv', $venv)
}
$venvPython = Join-Path $venv 'Scripts\python.exe'
Invoke-Native $venvPython @('-m', 'pip', 'install', '--disable-pip-version-check', '-q', '--upgrade', 'pip')
Invoke-Native $venvPython @('-m', 'pip', 'install', '--disable-pip-version-check', '-q', '-r', (Join-Path $backendDest 'requirements.txt'))

# --- 5. Camera settings -----------------------------------------------------------
Write-Step "Camera: $Camera"
[Environment]::SetEnvironmentVariable('SNAPTASTIC_CAMERA', $Camera, 'Machine')
[Environment]::SetEnvironmentVariable('SNAPTASTIC_WEBCAM_INDEX', "$WebcamIndex", 'Machine')
if ($Camera -eq 'fuji' -and -not (Test-Path (Join-Path $backendDest 'camera\dll\XAPI.dll'))) {
    Write-Warning "No XAPI.dll in $backendDest\camera\dll. Copy the Fujifilm SDK DLLs into backend\camera\dll in the repo and re-run."
}

# --- 6. Scheduled task -------------------------------------------------------------
Write-Step "Registering the '$TaskName' task for $KioskUser"
$action = New-ScheduledTaskAction -Execute (Join-Path $venv 'Scripts\pythonw.exe') `
    -Argument 'run.py' -WorkingDirectory $backendDest
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $KioskUser
# Interactive: runs inside the kiosk user's session (no stored password), which
# is where USB cameras are reliably available.
$principal = New-ScheduledTaskPrincipal -UserId $KioskUser -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) `
    -MultipleInstances IgnoreNew -StartWhenAvailable
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal `
    -Settings $settings -Description 'Snaptastic photo booth backend (http://localhost:8080)' -Force | Out-Null

Write-Host "`nDone." -ForegroundColor Green
Write-Host "The backend starts when $KioskUser signs in. To start it now (if you are $KioskUser):"
Write-Host "  Start-ScheduledTask -TaskName '$TaskName'"
Write-Host 'Then open http://localhost:8080, or try the kiosk view with:'
Write-Host "  powershell -ExecutionPolicy Bypass -File $InstallDir\kiosk\launch-kiosk-dev.ps1"
Write-Host 'Lock-down steps (Assigned Access): kiosk\windows\README.md'
