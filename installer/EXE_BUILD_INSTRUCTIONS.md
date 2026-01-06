# Watson EXE Installer Build Instructions

**Step-by-step guide to building the Watson Setup executable**

---

## Overview

The EXE installer uses **Inno Setup**, a free and simple installer creator that does not require .NET. This is the recommended method for most users.

| Component | Purpose | Download Size |
|-----------|---------|---------------|
| Python 3.9+ | Run Watson source code | ~25 MB |
| PyInstaller | Create Watson.exe | ~15 MB |
| Inno Setup | Create Setup installer | ~5 MB |

**Estimated total time:** 15-20 minutes

---

## Step 1: Install Python

### Download

1. Go to: https://www.python.org/downloads/
2. Click **Download Python 3.12.x** (or latest)
3. Run the installer

### Install

1. **IMPORTANT:** Check ☑ **"Add python.exe to PATH"**
2. Click **Install Now**
3. Wait for completion, then click **Close**

### Verify

Open a **new** PowerShell window:

```powershell
python --version
pip --version
```

---

## Step 2: Install PyInstaller

```powershell
pip install pyinstaller
```

Verify:
```powershell
pyinstaller --version
```

---

## Step 3: Install Inno Setup

### Download

1. Go to: https://jrsoftware.org/isdl.php
2. Click **"innosetup-6.x.x.exe"** (Stable Release)
3. Save and run the installer

### Install

1. Run the downloaded installer
2. Accept the license agreement
3. Use default installation path: `C:\Program Files (x86)\Inno Setup 6`
4. Check ☑ **"Install Inno Setup Preprocessor"**
5. Click **Install**
6. Click **Finish**

### Verify

The Inno Setup Compiler should now be available at:
```
C:\Program Files (x86)\Inno Setup 6\ISCC.exe
```

---

## Step 4: Install Watson Dependencies

Navigate to the Watson source folder:

```powershell
cd path\to\Watson_v1.3
pip install -r requirements.txt
```

---

## Step 5: Build Watson.exe

### Option A: Use the Build Script

```powershell
python build_installer.py
```

### Option B: Manual PyInstaller Command

```powershell
pyinstaller --onefile --windowed --name Watson main.py
```

### Verify

Check that the executable was created:
```powershell
dir dist\Watson.exe
```

You should see `Watson.exe` (approximately 50-80 MB).

---

## Step 6: Prepare Installer Files

Create the installer directory structure:

```powershell
# Create output directory
mkdir installer\output

# Copy the executable
copy dist\Watson.exe installer\

# Copy sample data
copy sample_data.csv installer\
```

### Create Icon File

You need a `watson_icon.ico` file in the `installer\` folder. 

If you do not have one, you can:
1. Use any .ico file and rename it to `watson_icon.ico`
2. Create one from a PNG using an online converter (search "PNG to ICO converter")
3. Skip the icon (edit Watson_Setup.iss to remove icon references)

### Final Directory Structure

```
Watson_v1.3/
├── installer/
│   ├── Watson_Setup.iss      ← Inno Setup script (provided)
│   ├── LICENSE.rtf           ← License file (provided)
│   ├── InfoBefore.txt        ← Pre-install info (provided)
│   ├── Watson.exe            ← Copy from dist\
│   ├── watson_icon.ico       ← You provide this
│   ├── sample_data.csv       ← Copy from root
│   └── output\               ← Installer will be created here
```

---

## Step 7: Build the Installer

### Option A: Using Inno Setup GUI

1. Open **Inno Setup Compiler** from Start Menu
2. Click **File → Open**
3. Navigate to `Watson_v1.3\installer\Watson_Setup.iss`
4. Click **Build → Compile** (or press F9)
5. Wait for compilation to complete
6. Find the installer in `installer\output\Watson_Setup_1.3.0.exe`

### Option B: Using Command Line

```powershell
cd Watson_v1.3\installer
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" Watson_Setup.iss
```

### Expected Output

```
Successful compile (X.XX sec). Resulting Setup program filename is:
C:\...\Watson_v1.3\installer\output\Watson_Setup_1.3.0.exe
```

---

## Step 8: Test the Installer

1. Navigate to `installer\output\`
2. Double-click `Watson_Setup_1.3.0.exe`
3. Follow the installation wizard
4. Launch Watson from the Start Menu or Desktop shortcut
5. Verify the application runs correctly

### Test Uninstall

1. Go to **Settings → Apps → Installed Apps**
2. Find **WATSON**
3. Click **Uninstall**
4. Verify clean removal

---

## Complete Build Script

Save this as `Build-EXE-Installer.ps1` in the Watson_v1.3 folder:

```powershell
# Build-EXE-Installer.ps1
# Complete Watson EXE Installer Build Script

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Watson EXE Installer Build" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check for Inno Setup
$InnoPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $InnoPath)) {
    Write-Host "ERROR: Inno Setup not found at $InnoPath" -ForegroundColor Red
    Write-Host "Download from: https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
    exit 1
}

# Step 1: Install dependencies
Write-Host "`n[1/4] Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Step 2: Build executable
Write-Host "`n[2/4] Building Watson.exe..." -ForegroundColor Yellow
pyinstaller --onefile --windowed --name Watson main.py

if (-not (Test-Path "dist\Watson.exe")) {
    Write-Host "ERROR: Watson.exe was not created!" -ForegroundColor Red
    exit 1
}
Write-Host "  Watson.exe created successfully" -ForegroundColor Green

# Step 3: Copy files to installer directory
Write-Host "`n[3/4] Preparing installer files..." -ForegroundColor Yellow
Copy-Item "dist\Watson.exe" "installer\" -Force
Copy-Item "sample_data.csv" "installer\" -Force

if (-not (Test-Path "installer\output")) {
    New-Item -ItemType Directory -Path "installer\output" | Out-Null
}

# Check for icon
if (-not (Test-Path "installer\watson_icon.ico")) {
    Write-Host "  WARNING: watson_icon.ico not found" -ForegroundColor Yellow
    Write-Host "           Installer may fail without icon file" -ForegroundColor Yellow
}

# Step 4: Build installer
Write-Host "`n[4/4] Building setup installer..." -ForegroundColor Yellow
Push-Location "installer"
try {
    & $InnoPath "Watson_Setup.iss"
    
    if (Test-Path "output\Watson_Setup_1.3.0.exe") {
        $size = (Get-Item "output\Watson_Setup_1.3.0.exe").Length / 1MB
        Write-Host "`n========================================" -ForegroundColor Green
        Write-Host "  BUILD SUCCESSFUL!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  Output: installer\output\Watson_Setup_1.3.0.exe" -ForegroundColor White
        Write-Host "  Size: $([math]::Round($size, 2)) MB" -ForegroundColor White
    }
} finally {
    Pop-Location
}
```

Run with:
```powershell
.\Build-EXE-Installer.ps1
```

---

## Troubleshooting

### "python is not recognized"

Python was not added to PATH. Reinstall Python and check ☑ "Add python.exe to PATH".

### "pyinstaller is not recognized"

```powershell
# Try running via Python module
python -m PyInstaller --onefile --windowed --name Watson main.py
```

### "ISCC.exe not found"

Verify Inno Setup installation path:
```powershell
dir "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
```

If installed elsewhere, update the path in the build script.

### Antivirus blocks Watson.exe

Some antivirus software flags PyInstaller executables as false positives. Options:
1. Add an exclusion for the build folder
2. Submit the file to your antivirus vendor as a false positive
3. Sign the executable with a code signing certificate

### Missing icon file

If you do not have `watson_icon.ico`, edit `Watson_Setup.iss`:
1. Open in text editor
2. Comment out or remove these lines:
   ```
   SetupIconFile=watson_icon.ico
   UninstallDisplayIcon={app}\Watson.exe
   ```
3. Remove icon reference from `[Icons]` section

---

## Quick Reference

| Step | Command |
|------|---------|
| Install PyInstaller | `pip install pyinstaller` |
| Install dependencies | `pip install -r requirements.txt` |
| Build Watson.exe | `python build_installer.py` |
| Build installer (GUI) | Open Inno Setup → File → Open → Watson_Setup.iss → Build → Compile |
| Build installer (CLI) | `& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\Watson_Setup.iss` |

---

## Output

After successful build:

| File | Location | Purpose |
|------|----------|---------|
| Watson.exe | `dist\` | Standalone executable |
| Watson_Setup_1.3.0.exe | `installer\output\` | Installer for distribution |

---

*Copyright © 2025 A Step in the Right Direction LLC. All Rights Reserved.*
