# CIVIQUAL MSI Build Script
# Copyright (c) 2025 A Step in the Right Direction LLC
# 
# This script builds the CiviQual MSI installer using WiX Toolset v4
#
# Prerequisites:
#   1. .NET SDK 6.0 or later installed
#   2. WiX Toolset v4 installed: dotnet tool install --global wix
#   3. PyInstaller-built CiviQual.exe in Files\ directory
#
# Usage:
#   .\Build-MSI.ps1
#   .\Build-MSI.ps1 -Version "1.3.1"

param(
    [string]$Version = "1.3.0"
)

$ErrorActionPreference = "Stop"

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  CIVIQUAL MSI Installer Build Script" -ForegroundColor Cyan
Write-Host "  Version: $Version" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Check for WiX
Write-Host "Checking for WiX Toolset..." -ForegroundColor Yellow
$wixInstalled = $null
try {
    $wixInstalled = wix --version 2>$null
} catch {
    $wixInstalled = $null
}

if (-not $wixInstalled) {
    Write-Host "ERROR: WiX Toolset v4 not found!" -ForegroundColor Red
    Write-Host "Install with: dotnet tool install --global wix" -ForegroundColor Yellow
    Write-Host "Then restart PowerShell and try again." -ForegroundColor Yellow
    exit 1
}
Write-Host "  Found WiX: $wixInstalled" -ForegroundColor Green

# Check for required files
Write-Host ""
Write-Host "Checking required files..." -ForegroundColor Yellow

$requiredFiles = @(
    "CiviQual.wxs",
    "LICENSE.rtf",
    "civiqual_icon.ico",
    "Files\CiviQual.exe",
    "Files\civiqual_icon.png",
    "Files\sample_data.csv",
    "Files\README.md",
    "Files\LICENSE",
    "Files\SECTION_508_COMPLIANCE.md"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  [OK] $file" -ForegroundColor Green
    } else {
        Write-Host "  [MISSING] $file" -ForegroundColor Red
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "ERROR: Missing required files. Cannot build MSI." -ForegroundColor Red
    Write-Host ""
    Write-Host "To prepare files:" -ForegroundColor Yellow
    Write-Host "  1. Build CiviQual.exe using PyInstaller" -ForegroundColor Yellow
    Write-Host "  2. Copy all required files to Files\ directory" -ForegroundColor Yellow
    Write-Host "  3. Ensure civiqual_icon.ico exists in current directory" -ForegroundColor Yellow
    exit 1
}

# Build MSI
Write-Host ""
Write-Host "Building MSI installer..." -ForegroundColor Yellow

$outputFile = "CiviQual_$Version.msi"

try {
    wix build CiviQual.wxs -o $outputFile -ext WixToolset.UI.wixext
    
    if (Test-Path $outputFile) {
        $fileInfo = Get-Item $outputFile
        Write-Host ""
        Write-Host "=============================================" -ForegroundColor Green
        Write-Host "  BUILD SUCCESSFUL!" -ForegroundColor Green
        Write-Host "=============================================" -ForegroundColor Green
        Write-Host "  Output: $outputFile" -ForegroundColor White
        Write-Host "  Size: $([math]::Round($fileInfo.Length / 1MB, 2)) MB" -ForegroundColor White
        Write-Host ""
        Write-Host "Deployment Commands:" -ForegroundColor Cyan
        Write-Host "  Interactive:    msiexec /i $outputFile" -ForegroundColor White
        Write-Host "  Silent:         msiexec /i $outputFile /qn" -ForegroundColor White
        Write-Host "  With Log:       msiexec /i $outputFile /qn /l*v civiqual_install.log" -ForegroundColor White
        Write-Host "  Uninstall:      msiexec /x $outputFile /qn" -ForegroundColor White
    } else {
        Write-Host "ERROR: MSI file was not created." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "ERROR: Build failed!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
