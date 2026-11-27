<#
.SYNOPSIS
    Automated One-Click Installer for Termux Sentinel on Windows Terminal & PowerShell.
.DESCRIPTION
    Installs Termux Sentinel as a native CLI/TUI command for Windows Command Prompt,
    PowerShell 5.1/7+, and Windows Terminal.
#>

[CmdletBinding()]
param(
    [switch]$Force
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " 🛡️  SENTINEL CLI/TUI - WINDOWS ONE-TAP INSTALLER" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Python 3.9+
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
}

if (-not $pythonCmd) {
    Write-Error "Python is not found in your PATH! Please install Python 3.9+ from https://python.org or via 'winget install Python.Python.3.12'."
    exit 1
}

$pyVer = & $pythonCmd.Source -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
Write-Host "[✓] Found Python $pyVer ($($pythonCmd.Source))" -ForegroundColor Green

# 2. Setup AppData and Vault
$appDataDir = [System.IO.Path]::Combine($env:APPDATA, "termux_sentinel")
if (-not (Test-Path $appDataDir)) {
    New-Item -ItemType Directory -Path $appDataDir -Force | Out-Null
}

$vaultFile = [System.IO.Path]::Combine($appDataDir, "vault.json")
$srcVault = [System.IO.Path]::Combine($PSScriptRoot, "vault.json")
if (-not (Test-Path $vaultFile) -and (Test-Path $srcVault)) {
    Copy-Item -Path $srcVault -Destination $vaultFile -Force
    Write-Host "[✓] Initialized Preservation Vault: $vaultFile" -ForegroundColor Green
}

# 3. Install Package via pip in editable mode
Write-Host "[*] Registering 'sentinel' global console script..." -ForegroundColor Yellow
& $pythonCmd.Source -m pip install -e "$PSScriptRoot" --no-deps --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Warning "pip install failed or requires elevation. Creating fallback batch shims..."
}

# 4. Create fallback shims in User Local Bin
$localBin = [System.IO.Path]::Combine($env:USERPROFILE, ".local", "bin")
if (-not (Test-Path $localBin)) {
    New-Item -ItemType Directory -Path $localBin -Force | Out-Null
}

$pyScript = [System.IO.Path]::Combine($PSScriptRoot, "Termux_Sentinel.py")
$shimCmd = "@echo off`r`npython `"$pyScript`" %*`r`n"
Set-Content -Path (Join-Path $localBin "sentinel.cmd") -Value $shimCmd -Encoding ASCII
Set-Content -Path (Join-Path $localBin "termux-sentinel.cmd") -Value $shimCmd -Encoding ASCII

# Ensure $localBin is in User PATH
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$localBin*") {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$localBin", "User")
    $env:Path = "$env:Path;$localBin"
    Write-Host "[✓] Added '$localBin' to User PATH environment variable." -ForegroundColor Green
}

# 5. Register PowerShell Profile Function
if ($PROFILE) {
    $profileDir = Split-Path $PROFILE
    if (-not (Test-Path $profileDir)) {
        New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
    }
    $funcDef = "`r`nfunction sentinel { & python `"$pyScript`" @args }`r`nfunction termux-sentinel { & python `"$pyScript`" @args }`r`n"
    if (Test-Path $PROFILE) {
        $content = Get-Content $PROFILE -Raw
        if ($content -notlike "*function sentinel*") {
            Add-Content -Path $PROFILE -Value $funcDef
            Write-Host "[✓] Added 'sentinel' alias to PowerShell Profile ($PROFILE)" -ForegroundColor Green
        }
    } else {
        Set-Content -Path $PROFILE -Value $funcDef
        Write-Host "[✓] Created PowerShell Profile with 'sentinel' alias." -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " ✓ Installation Complete! You can now run:" -ForegroundColor Green
Write-Host "     sentinel           (Interactive Responsive Cyber TUI)" -ForegroundColor White
Write-Host "     sentinel status    (Live Telemetry HUD)" -ForegroundColor White
Write-Host "     sentinel hunt      (Scan Large Directories)" -ForegroundColor White
Write-Host "     sentinel help      (CLI Manual)" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Cyan
