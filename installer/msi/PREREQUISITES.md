# CiviQual Stats MSI Build Prerequisites

**Step-by-step installation guide for all required tools**

---

## Overview

Building the CiviQual Stats MSI installer requires these components:

| Component | Purpose | Download Size |
|-----------|---------|---------------|
| Python 3.9+ | Run CiviQual Stats source code | ~25 MB |
| .NET SDK 6.0+ | Required for WiX Toolset | ~200 MB |
| WiX Toolset v4 | Build MSI installer | ~5 MB |
| PyInstaller | Create CiviQualStats.exe | ~15 MB |

**Estimated total time:** 15-20 minutes

---

## Step 1: Install Python 3.9 or Later

### Download

1. Go to: https://www.python.org/downloads/
2. Click **Download Python 3.12.x** (or latest version)
3. Save the installer (e.g., `python-3.12.0-amd64.exe`)

### Install

1. **Run the installer**
2. **IMPORTANT:** Check ☑ **"Add python.exe to PATH"** at the bottom
3. Click **"Install Now"** for default installation
   - Or click "Customize installation" if you need specific options
4. Wait for installation to complete
5. Click **Close**

### Verify Installation

Open a **new** PowerShell or Command Prompt window:

```powershell
python --version
```

Expected output:
```
Python 3.12.0
```

Also verify pip (Python package manager):
```powershell
pip --version
```

Expected output:
```
pip 23.2.1 from C:\Users\...\site-packages\pip (python 3.12)
```

### Troubleshooting

**"python is not recognized"**
- Close and reopen PowerShell/Command Prompt
- If still not working, Python was not added to PATH. Reinstall and check the PATH option.

**Alternative:** Add Python to PATH manually:
1. Search Windows for "Environment Variables"
2. Click "Environment Variables..."
3. Under "User variables", select "Path" and click "Edit"
4. Click "New" and add: `C:\Users\<YourUsername>\AppData\Local\Programs\Python\Python312\`
5. Click "New" again and add: `C:\Users\<YourUsername>\AppData\Local\Programs\Python\Python312\Scripts\`
6. Click OK to save

---

## Step 2: Install .NET SDK 6.0 or Later

### Download

1. Go to: https://dotnet.microsoft.com/download
2. Under ".NET SDK", click **Download .NET SDK x64**
   - Choose the latest LTS version (e.g., .NET 8.0)
3. Save the installer (e.g., `dotnet-sdk-8.0.100-win-x64.exe`)

### Install

1. **Run the installer**
2. Click **Install**
3. If prompted by User Account Control, click **Yes**
4. Wait for installation to complete
5. Click **Close**

### Verify Installation

Open a **new** PowerShell window:

```powershell
dotnet --version
```

Expected output:
```
8.0.100
```

### Troubleshooting

**"dotnet is not recognized"**
- Close and reopen PowerShell
- Restart your computer if the command still is not found

---

## Step 3: Install WiX Toolset v4

WiX (Windows Installer XML) is installed as a .NET global tool.

### Install WiX

Open PowerShell and run:

```powershell
dotnet tool install --global wix
```

Expected output:
```
You can invoke the tool using the following command: wix
Tool 'wix' (version '4.0.x') was successfully installed.
```

### Install WiX UI Extension

The UI extension provides the standard installation wizard dialogs:

```powershell
wix extension add WixToolset.UI.wixext
```

Expected output:
```
WixToolset.UI.wixext was added.
```

### Verify Installation

```powershell
wix --version
```

Expected output:
```
wix version 4.0.x
```

List installed extensions:
```powershell
wix extension list
```

Expected output should include:
```
WixToolset.UI.wixext    4.0.x
```

### Troubleshooting

**"wix is not recognized"**
- Close and reopen PowerShell
- The .NET tools path may not be in your PATH. Add it:
  ```powershell
  $env:PATH += ";$env:USERPROFILE\.dotnet\tools"
  ```
- To make permanent, add `%USERPROFILE%\.dotnet\tools` to your system PATH

**"Extension not found" when building**
- Run the extension add command again:
  ```powershell
  wix extension add WixToolset.UI.wixext
  ```

---

## Step 4: Install PyInstaller

PyInstaller converts Python applications into standalone executables.

### Install via pip

```powershell
pip install pyinstaller
```

Expected output:
```
Successfully installed pyinstaller-6.x.x ...
```

### Verify Installation

```powershell
pyinstaller --version
```

Expected output:
```
6.3.0
```

### Troubleshooting

**"pyinstaller is not recognized"**
- Ensure Python Scripts folder is in PATH (see Step 1 troubleshooting)
- Try running with full path:
  ```powershell
  python -m PyInstaller --version
  ```

---

## Step 5: Install CiviQual Stats Python Dependencies

Navigate to the CiviQual Stats source directory and install required packages:

```powershell
cd path\to\CiviQual
pip install -r requirements.txt
```

This installs:
- PySide6 (GUI framework)
- pandas (data analysis)
- numpy (numerical computing)
- scipy (statistical functions)
- matplotlib (charting)
- python-docx (Word document generation)
- openpyxl (Excel file support)

### Verify Key Packages

```powershell
pip list | findstr -i "pyside pandas numpy scipy matplotlib"
```

---

## Verification Checklist

Run these commands to verify all prerequisites are installed:

```powershell
Write-Host "Checking prerequisites..." -ForegroundColor Cyan

# Python
Write-Host "`n[1] Python:" -ForegroundColor Yellow
python --version

# .NET SDK
Write-Host "`n[2] .NET SDK:" -ForegroundColor Yellow
dotnet --version

# WiX
Write-Host "`n[3] WiX Toolset:" -ForegroundColor Yellow
wix --version

# WiX Extensions
Write-Host "`n[4] WiX Extensions:" -ForegroundColor Yellow
wix extension list

# PyInstaller
Write-Host "`n[5] PyInstaller:" -ForegroundColor Yellow
pyinstaller --version

Write-Host "`nAll prerequisites checked!" -ForegroundColor Green
```

Save as `Check-Prerequisites.ps1` and run:
```powershell
.\Check-Prerequisites.ps1
```

### Expected Output

```
Checking prerequisites...

[1] Python:
Python 3.12.0

[2] .NET SDK:
8.0.100

[3] WiX Toolset:
wix version 4.0.4

[4] WiX Extensions:
WixToolset.UI.wixext    4.0.4

[5] PyInstaller:
6.3.0

All prerequisites checked!
```

---

## Quick Reference Card

| Tool | Install Command | Verify Command |
|------|-----------------|----------------|
| Python | Download from python.org | `python --version` |
| .NET SDK | Download from dotnet.microsoft.com | `dotnet --version` |
| WiX Toolset | `dotnet tool install --global wix` | `wix --version` |
| WiX UI Extension | `wix extension add WixToolset.UI.wixext` | `wix extension list` |
| PyInstaller | `pip install pyinstaller` | `pyinstaller --version` |
| CiviQual Stats dependencies | `pip install -r requirements.txt` | `pip list` |

---

## Next Steps

Once all prerequisites are installed, proceed to **BUILD_INSTRUCTIONS.md** to build the CiviQual Stats MSI installer.

---

## System Requirements

| Requirement | Minimum |
|-------------|---------|
| Operating System | Windows 10 64-bit or later |
| RAM | 4 GB (8 GB recommended) |
| Disk Space | 2 GB free (for tools and build output) |
| Internet | Required for downloads |

---

*Copyright © 2026 A Step in the Right Direction LLC. All Rights Reserved.*
