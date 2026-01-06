# Watson MSI Build Instructions

**Version 1.3.0** | Step-by-step guide to building the Watson MSI installer

---

## Prerequisites

### 1. Install Python 3.9 or Later

Download from: https://www.python.org/downloads/

Verify installation:
```powershell
python --version
```

### 2. Install .NET SDK 6.0 or Later

Download from: https://dotnet.microsoft.com/download

Verify installation:
```powershell
dotnet --version
```

### 3. Install WiX Toolset v4

```powershell
dotnet tool install --global wix
```

Verify installation:
```powershell
wix --version
```

### 4. Install WiX UI Extension

```powershell
wix extension add WixToolset.UI.wixext
```

### 5. Install PyInstaller

```powershell
pip install pyinstaller
```

---

## Step 1: Prepare the Source Files

Ensure you have the complete Watson v1.3 source package with this structure:

```
Watson_v1.3/
├── main.py
├── statistics_engine.py
├── visualizations.py
├── data_handler.py
├── report_generator.py
├── process_diagrams.py
├── build_installer.py
├── requirements.txt
├── sample_data.csv
├── README.md
├── LICENSE
├── SECTION_508_COMPLIANCE.md
└── installer/
    └── msi/
        ├── Watson.wxs
        ├── Build-MSI.ps1
        └── LICENSE.rtf
```

---

## Step 2: Install Python Dependencies

```powershell
cd Watson_v1.3
pip install -r requirements.txt
```

---

## Step 3: Build Watson.exe with PyInstaller

### Option A: Use the Build Script (Recommended)

```powershell
python build_installer.py
```

This creates `dist/Watson.exe`

### Option B: Manual PyInstaller Command

```powershell
pyinstaller --onefile --windowed --name Watson --icon=watson_icon.ico main.py
```

### Verify the Build

```powershell
# Check that Watson.exe was created
dir dist\Watson.exe
```

---

## Step 4: Prepare MSI Build Directory

Create the required directory structure for WiX:

```powershell
# Navigate to MSI directory
cd installer\msi

# Create Files subdirectory
mkdir Files

# Copy required files
copy ..\..\dist\Watson.exe Files\
copy ..\..\sample_data.csv Files\
copy ..\..\README.md Files\
copy ..\..\LICENSE Files\
copy ..\..\SECTION_508_COMPLIANCE.md Files\
```

### Create Icon Files

You need two icon files:

1. **watson_icon.ico** - Windows icon format (place in `installer\msi\`)
2. **watson_icon.png** - PNG format (place in `installer\msi\Files\`)

If you do not have icon files, you can create placeholder icons or download the Watson icon from the project repository.

### Final Directory Structure

```
installer/msi/
├── Watson.wxs
├── Build-MSI.ps1
├── LICENSE.rtf
├── watson_icon.ico          ← Windows icon
└── Files/
    ├── Watson.exe           ← PyInstaller output
    ├── watson_icon.png      ← PNG icon
    ├── sample_data.csv
    ├── README.md
    ├── LICENSE
    └── SECTION_508_COMPLIANCE.md
```

---

## Step 5: Build the MSI

### Option A: Use the Build Script (Recommended)

```powershell
cd installer\msi
.\Build-MSI.ps1
```

### Option B: Manual WiX Command

```powershell
cd installer\msi
wix build Watson.wxs -o Watson_1.3.0.msi -ext WixToolset.UI.wixext
```

### Expected Output

```
Watson_1.3.0.msi created successfully
```

---

## Step 6: Verify the MSI

### Test Interactive Installation

```powershell
msiexec /i Watson_1.3.0.msi
```

### Test Silent Installation

```powershell
msiexec /i Watson_1.3.0.msi /qn /l*v install_test.log
```

### Verify Installation

```powershell
# Check installed files
dir "${env:ProgramFiles}\Watson"

# Check Start Menu shortcut
dir "${env:APPDATA}\Microsoft\Windows\Start Menu\Programs\Watson"

# Launch application
& "${env:ProgramFiles}\Watson\Watson.exe"
```

### Test Uninstall

```powershell
msiexec /x Watson_1.3.0.msi /qn
```

---

## Complete Build Script

Save this as `Build-All.ps1` for a one-command build process:

```powershell
# Build-All.ps1 - Complete Watson MSI Build Script
# Run from Watson_v1.3 root directory

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Watson MSI Complete Build Process" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Step 1: Install dependencies
Write-Host "`n[1/5] Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Step 2: Build executable
Write-Host "`n[2/5] Building Watson.exe with PyInstaller..." -ForegroundColor Yellow
python build_installer.py

if (-not (Test-Path "dist\Watson.exe")) {
    Write-Host "ERROR: Watson.exe was not created!" -ForegroundColor Red
    exit 1
}

# Step 3: Prepare MSI directory
Write-Host "`n[3/5] Preparing MSI build directory..." -ForegroundColor Yellow
$msiDir = "installer\msi"
$filesDir = "$msiDir\Files"

if (-not (Test-Path $filesDir)) {
    New-Item -ItemType Directory -Path $filesDir | Out-Null
}

Copy-Item "dist\Watson.exe" "$filesDir\" -Force
Copy-Item "sample_data.csv" "$filesDir\" -Force
Copy-Item "README.md" "$filesDir\" -Force
Copy-Item "LICENSE" "$filesDir\" -Force
Copy-Item "SECTION_508_COMPLIANCE.md" "$filesDir\" -Force

# Step 4: Check for icon files
Write-Host "`n[4/5] Checking icon files..." -ForegroundColor Yellow
if (-not (Test-Path "$msiDir\watson_icon.ico")) {
    Write-Host "WARNING: watson_icon.ico not found. MSI build may fail." -ForegroundColor Yellow
    Write-Host "         Please add watson_icon.ico to $msiDir\" -ForegroundColor Yellow
}

if (-not (Test-Path "$filesDir\watson_icon.png")) {
    Write-Host "WARNING: watson_icon.png not found in Files directory." -ForegroundColor Yellow
    Write-Host "         Please add watson_icon.png to $filesDir\" -ForegroundColor Yellow
}

# Step 5: Build MSI
Write-Host "`n[5/5] Building MSI installer..." -ForegroundColor Yellow
Push-Location $msiDir
try {
    wix build Watson.wxs -o Watson_1.3.0.msi -ext WixToolset.UI.wixext
    
    if (Test-Path "Watson_1.3.0.msi") {
        $size = (Get-Item "Watson_1.3.0.msi").Length / 1MB
        Write-Host "`n========================================" -ForegroundColor Green
        Write-Host "  BUILD SUCCESSFUL!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  Output: $msiDir\Watson_1.3.0.msi" -ForegroundColor White
        Write-Host "  Size: $([math]::Round($size, 2)) MB" -ForegroundColor White
    }
} finally {
    Pop-Location
}
```

---

## Troubleshooting

### "WiX not found"

```powershell
# Reinstall WiX
dotnet tool install --global wix

# Restart PowerShell to refresh PATH
```

### "Extension not found"

```powershell
wix extension add WixToolset.UI.wixext
```

### "File not found" errors

Verify all files exist in the `Files\` subdirectory:
```powershell
dir installer\msi\Files\
```

### "ICE validation errors"

These are usually warnings and can often be ignored. To suppress:
```powershell
wix build Watson.wxs -o Watson_1.3.0.msi -ext WixToolset.UI.wixext -sice:ICE61
```

### PyInstaller antivirus false positives

Some antivirus software flags PyInstaller executables. Options:
1. Add exclusion for build directory
2. Sign the executable with a code signing certificate
3. Use `--onedir` instead of `--onefile` mode

---

## Summary of Commands

```powershell
# From Watson_v1.3 root directory:

# 1. Install dependencies
pip install -r requirements.txt

# 2. Build executable
python build_installer.py

# 3. Prepare files
cd installer\msi
mkdir Files
copy ..\..\dist\Watson.exe Files\
copy ..\..\sample_data.csv Files\
copy ..\..\README.md Files\
copy ..\..\LICENSE Files\
copy ..\..\SECTION_508_COMPLIANCE.md Files\

# 4. Build MSI (ensure watson_icon.ico and watson_icon.png exist)
wix build Watson.wxs -o Watson_1.3.0.msi -ext WixToolset.UI.wixext

# 5. Test
msiexec /i Watson_1.3.0.msi
```

---

## Output

After successful build, you will have:

| File | Description |
|------|-------------|
| `Watson_1.3.0.msi` | Windows Installer package for distribution |

This MSI can be used for:
- Individual installation (double-click)
- Silent deployment (`msiexec /i Watson_1.3.0.msi /qn`)
- Group Policy distribution
- SCCM/Intune deployment

---

*Copyright © 2025 A Step in the Right Direction LLC. All Rights Reserved.*
