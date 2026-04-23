# CiviQual Stats v2.0.0 - PyInstaller Build Script
# Run from repository root: C:\Users\jbper\OneDrive\Documents\GitHub\CiviQual
#
# This script:
#   1. Builds the standalone .exe with PyInstaller
#   2. Builds the MSI installer from committed WiX files
#      (CiviQualStats_Build.wxs + HarvestedFiles.wxs using WiX 5 <Files>)
#   3. Signs the MSI with your Certum certificate

param(
    [switch]$SkipPyInstaller,
    [switch]$SkipSign,
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

# Configuration
$RepoPath = "C:\Users\jbper\OneDrive\Documents\GitHub\CiviQual"
$Version = "2.0.0"
$Thumbprint = "E6830B627AF1AD8980FADDF221D27FAE361A166D"
$TimestampUrl = "http://time.certum.pl"

# Colors
function Write-Step { param($msg) Write-Host "`n=== $msg ===" -ForegroundColor Cyan }
function Write-Success { param($msg) Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Fail { param($msg) Write-Host "[ERROR] $msg" -ForegroundColor Red }

# Navigate to repo
Set-Location $RepoPath
Write-Step "CiviQual Stats v$Version Build"
Write-Host "Working directory: $RepoPath"

# ============================================================
# CLEAN (optional)
# ============================================================
if ($Clean) {
    Write-Step "Cleaning previous build artifacts"
    
    $cleanPaths = @("build", "dist", "*.msi", "*.wixpdb", "__pycache__")
    foreach ($path in $cleanPaths) {
        if (Test-Path $path) {
            Remove-Item -Path $path -Recurse -Force
            Write-Host "  Removed: $path"
        }
    }
    Write-Success "Clean complete"
}

# ============================================================
# STEP 1: Verify Prerequisites
# ============================================================
Write-Step "Verifying prerequisites"

# Check Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Fail "Python not found in PATH"
    exit 1
}
Write-Success "Python: $($python.Source)"

# Check PyInstaller
$pyinstaller = Get-Command pyinstaller -ErrorAction SilentlyContinue
if (-not $pyinstaller) {
    Write-Warn "PyInstaller not found. Installing..."
    pip install pyinstaller
}
Write-Success "PyInstaller: $(pyinstaller --version)"

# Check WiX
$wix = Get-Command wix -ErrorAction SilentlyContinue
if (-not $wix) {
    Write-Fail "WiX not found. Install with: winget install WixToolset.WiX"
    exit 1
}
Write-Success "WiX: $(wix --version)"

# Check signtool
$signtoolPaths = Get-ChildItem "C:\Program Files (x86)\Windows Kits\10\bin\10.*\x64\signtool.exe" -ErrorAction SilentlyContinue
if (-not $signtoolPaths -and -not $SkipSign) {
    Write-Warn "signtool not found. MSI will not be signed."
    $SkipSign = $true
} else {
    $signtool = ($signtoolPaths | Sort-Object | Select-Object -Last 1).FullName
    Write-Success "signtool: $signtool"
}

# Check required files
$requiredFiles = @(
    "main.py",
    "civiqual_icon.ico",
    "CiviQualStats.spec",
    "version_info.txt",
    "CiviQualStats_Build.wxs",
    "HarvestedFiles.wxs"
)
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Fail "Required file missing: $file"
        exit 1
    }
}
Write-Success "All required files present"

# ============================================================
# STEP 2: Build with PyInstaller
# ============================================================
if (-not $SkipPyInstaller) {
    Write-Step "Building executable with PyInstaller"
    
    # Clean previous build
    if (Test-Path "dist") {
        Remove-Item -Path "dist" -Recurse -Force
    }
    if (Test-Path "build") {
        Remove-Item -Path "build" -Recurse -Force
    }
    
    # Run PyInstaller
    Write-Host "Running: pyinstaller CiviQualStats.spec"
    pyinstaller CiviQualStats.spec
    
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "PyInstaller build failed"
        exit 1
    }
    
    # Verify output
    $exePath = "dist\CiviQualStats\CiviQualStats.exe"
    if (Test-Path $exePath) {
        $exeInfo = Get-Item $exePath
        Write-Success "Executable created: $exePath ($([math]::Round($exeInfo.Length / 1MB, 2)) MB)"
    } else {
        Write-Fail "Executable not found at $exePath"
        exit 1
    }
    
    # List output folder size
    $distSize = (Get-ChildItem "dist\CiviQualStats" -Recurse | Measure-Object -Property Length -Sum).Sum
    Write-Host "Total dist size: $([math]::Round($distSize / 1MB, 2)) MB"
    
} else {
    Write-Step "Skipping PyInstaller (using existing dist folder)"
    if (-not (Test-Path "dist\CiviQualStats\CiviQualStats.exe")) {
        Write-Fail "dist\CiviQualStats\CiviQualStats.exe not found. Run without -SkipPyInstaller"
        exit 1
    }
}

# ============================================================
# STEP 3: Build MSI
# ============================================================
Write-Step "Building MSI installer"

$msiName = "CiviQual_$Version.msi"

# Remove old MSI
if (Test-Path $msiName) {
    Remove-Item $msiName -Force
}

# Build with both WiX files
Write-Host "Running: wix build CiviQualStats_Build.wxs HarvestedFiles.wxs ..."
wix build CiviQualStats_Build.wxs HarvestedFiles.wxs `
    -d DistDir="dist\CiviQualStats" `
    -o $msiName

if ($LASTEXITCODE -ne 0) {
    Write-Fail "WiX build failed"
    exit 1
}

if (Test-Path $msiName) {
    $msiInfo = Get-Item $msiName
    Write-Success "MSI created: $msiName ($([math]::Round($msiInfo.Length / 1MB, 2)) MB)"
} else {
    Write-Fail "MSI not created"
    exit 1
}

# ============================================================
# STEP 4: Sign MSI
# ============================================================
if (-not $SkipSign) {
    Write-Step "Signing MSI with Certum certificate"
    
    Write-Host "Running: signtool sign ..."
    & $signtool sign `
        /sha1 $Thumbprint `
        /fd SHA256 `
        /tr $TimestampUrl `
        /td SHA256 `
        /d "CiviQual Stats $Version" `
        $msiName
    
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Signing failed"
        exit 1
    }
    
    # Verify signature
    Write-Host "`nVerifying signature..."
    $sig = Get-AuthenticodeSignature $msiName
    if ($sig.Status -eq "Valid") {
        Write-Success "Signature valid"
        Write-Host "  Signer: $($sig.SignerCertificate.Subject)"
        Write-Host "  Timestamp: $($sig.TimeStamperCertificate.Subject)"
    } else {
        Write-Warn "Signature status: $($sig.Status)"
    }
} else {
    Write-Step "Skipping MSI signing"
}

# ============================================================
# SUMMARY
# ============================================================
Write-Step "Build Complete"

Write-Host "`nOutput files:"
Write-Host "  - $msiName (installer)"
Write-Host "  - dist\CiviQualStats\CiviQualStats.exe (standalone executable)"

Write-Host "`nNext steps:"
Write-Host "  1. Test: Start-Process .\dist\CiviQualStats\CiviQualStats.exe"
Write-Host "  2. Test MSI: Start-Process msiexec.exe -ArgumentList '/i $msiName'"
Write-Host "  3. Git: git add -A && git commit -m 'Release v$Version'"
Write-Host "  4. Tag: git tag -a v$Version -m 'CiviQual Stats v$Version'"
Write-Host "  5. Push: git push origin main && git push origin v$Version"

Write-Host "`n"
