# WATSON MSI Deployment Guide

**Version 1.3.0** | Copyright © 2025 A Step in the Right Direction LLC

---

## Overview

This guide provides instructions for building and deploying WATSON using Windows Installer (MSI) technology. MSI deployment supports both individual users and enterprise environments:

**For Individual Users:**
- Standard Windows installer wizard (double-click to install)
- Add/Remove Programs integration
- Clean uninstall capability
- Windows Installer repair function

**For Enterprise Deployment:**
- Silent installation for mass deployment
- Group Policy distribution
- Microsoft Endpoint Configuration Manager (SCCM/MECM)
- Microsoft Intune
- Standardized uninstall process
- Windows Installer rollback capability

---

## Individual Installation

### Interactive Installation (Recommended for Individual Users)

Simply double-click `Watson_1.3.0.msi` to launch the installation wizard:

1. **Welcome Screen** - Click Next
2. **License Agreement** - Review and accept the license terms
3. **Installation Folder** - Accept default or choose custom location
   - Default: `C:\Program Files\Watson`
4. **Ready to Install** - Click Install
5. **Completion** - Click Finish

### Interactive Installation via Command Line

```powershell
msiexec /i Watson_1.3.0.msi
```

### Modify Installation

To change or repair the installation:
```powershell
msiexec /f Watson_1.3.0.msi
```

Or use **Settings → Apps → Installed Apps → WATSON → Modify**

### Uninstall

**Option 1:** Settings → Apps → Installed Apps → WATSON → Uninstall

**Option 2:** Command line:
```powershell
msiexec /x Watson_1.3.0.msi
```

---

## Choosing Between EXE and MSI Installers

| Feature | EXE Installer | MSI Installer |
|---------|---------------|---------------|
| **Best For** | Home users | Individual or Enterprise |
| **Installation** | Double-click | Double-click or command line |
| **Silent Install** | Limited | Full support |
| **Group Policy** | No | Yes |
| **SCCM/Intune** | Limited | Full support |
| **Repair Option** | No | Yes |
| **Rollback** | No | Yes |
| **Add/Remove Programs** | Yes | Yes |

**Recommendation:** 
- Home users can use either installer
- Corporate/government users should prefer MSI for standardized deployment and management

---

## Building the MSI Installer

### Prerequisites

1. **Windows 10/11** development machine
2. **.NET SDK 6.0 or later** - [Download](https://dotnet.microsoft.com/download)
3. **WiX Toolset v4** - Install via .NET CLI:
   ```powershell
   dotnet tool install --global wix
   ```
4. **Watson.exe** built via PyInstaller

### Directory Structure

Prepare the following structure before building:

```
Watson_MSI/
├── Watson.wxs              # WiX source file (provided)
├── Build-MSI.ps1           # Build script (provided)
├── LICENSE.rtf             # License in RTF format
├── watson_icon.ico         # Application icon
└── Files/
    ├── Watson.exe          # PyInstaller-built executable
    ├── watson_icon.png     # Icon file
    ├── sample_data.csv     # Sample data
    ├── README.md           # Documentation
    ├── LICENSE             # License text
    └── SECTION_508_COMPLIANCE.md
```

### Build Commands

**Using the Build Script (Recommended):**
```powershell
cd Watson_MSI
.\Build-MSI.ps1
```

**Manual Build with WiX v4:**
```powershell
wix build Watson.wxs -o Watson_1.3.0.msi -ext WixToolset.UI.wixext
```

**Manual Build with WiX v3 (Legacy):**
```powershell
candle.exe Watson.wxs -ext WixUIExtension
light.exe Watson.wixobj -ext WixUIExtension -o Watson_1.3.0.msi
```

---

## Installation Commands

### Interactive Installation
```powershell
msiexec /i Watson_1.3.0.msi
```

### Silent Installation
```powershell
msiexec /i Watson_1.3.0.msi /qn
```

### Silent with Logging
```powershell
msiexec /i Watson_1.3.0.msi /qn /l*v C:\Logs\watson_install.log
```

### Custom Installation Path
```powershell
msiexec /i Watson_1.3.0.msi /qn INSTALLFOLDER="D:\Apps\Watson"
```

### Repair Installation
```powershell
msiexec /f Watson_1.3.0.msi
```

### Silent Uninstall
```powershell
msiexec /x Watson_1.3.0.msi /qn
```

### Uninstall by Product Code
```powershell
msiexec /x {E8F9A1B2-C3D4-5E6F-7A8B-9C0D1E2F3A4B} /qn
```

---

## Group Policy Deployment

### Step-by-Step Instructions

1. **Copy MSI to Network Share**
   ```
   \\server\share\Software\Watson\Watson_1.3.0.msi
   ```
   Ensure the share has read permissions for target computers.

2. **Open Group Policy Management Console**
   - Press `Win + R`, type `gpmc.msc`, press Enter

3. **Create or Edit GPO**
   - Right-click the target OU → **Create a GPO in this domain**
   - Name: "Watson 1.3.0 Deployment"

4. **Configure Software Installation**
   - Navigate to: `Computer Configuration → Policies → Software Settings → Software Installation`
   - Right-click → **New → Package**
   - Browse to the network share and select `Watson_1.3.0.msi`
   - Select **Assigned** for automatic installation

5. **Configure Options (Optional)**
   - Right-click the package → **Properties**
   - **Deployment tab**: Select "Uninstall when out of scope"
   - **Upgrades tab**: Configure upgrade relationships

6. **Link and Test**
   - Link GPO to target OU
   - Run `gpupdate /force` on a test machine
   - Restart the machine to trigger installation

### GPO Troubleshooting

Check installation logs:
```powershell
Get-WinEvent -LogName "Application" | Where-Object {$_.ProviderName -eq "MsiInstaller"} | Select-Object -First 10
```

---

## Microsoft Endpoint Configuration Manager (SCCM/MECM)

### Create Application

1. **Navigate to**: Software Library → Application Management → Applications
2. **Create Application** → Windows Installer (*.msi)
3. **Browse** to `Watson_1.3.0.msi`
4. **Detection Method**: MSI Product Code `{E8F9A1B2-C3D4-5E6F-7A8B-9C0D1E2F3A4B}`

### Deployment Type Settings

| Setting | Value |
|---------|-------|
| Installation Program | `msiexec /i "Watson_1.3.0.msi" /qn` |
| Uninstall Program | `msiexec /x {E8F9A1B2-C3D4-5E6F-7A8B-9C0D1E2F3A4B} /qn` |
| Installation Behavior | Install for system |
| Logon Requirement | Whether or not a user is logged on |
| Installation Time | Maximum 15 minutes |

### Detection Rule

| Property | Value |
|----------|-------|
| Type | Windows Installer |
| Product Code | {E8F9A1B2-C3D4-5E6F-7A8B-9C0D1E2F3A4B} |

---

## Microsoft Intune Deployment

### Add Line-of-Business App

1. **Navigate to**: Microsoft Endpoint Manager admin center → Apps → All apps
2. **Add** → App type: **Line-of-business app**
3. **Select** the `Watson_1.3.0.msi` file
4. **Configure App Information**:
   - Name: WATSON
   - Description: Statistical Analysis Tool for Lean Six Sigma
   - Publisher: A Step in the Right Direction LLC
   - App Version: 1.3.0

### Command-Line Arguments

| Setting | Value |
|---------|-------|
| Command-line arguments | `/qn` |
| Ignore MSI app version | No |

### Assignment

1. **Assignments** → Add group
2. Select target groups
3. Choose assignment type: **Required** or **Available**

---

## Package Properties

| Property | Value |
|----------|-------|
| Product Name | WATSON |
| Product Version | 1.3.0.0 |
| Product Code | {E8F9A1B2-C3D4-5E6F-7A8B-9C0D1E2F3A4B} |
| Upgrade Code | E8F9A1B2-C3D4-5E6F-7A8B-9C0D1E2F3A4B |
| Manufacturer | A Step in the Right Direction LLC |
| Install Scope | Per-machine |
| Install Location | %ProgramFiles%\Watson |

---

## Registry Keys

After installation, the following registry keys are created:

**HKEY_CURRENT_USER\Software\AStepInTheRightDirection\Watson**
| Value | Type | Data |
|-------|------|------|
| InstallPath | REG_SZ | [Installation Directory] |
| Version | REG_SZ | 1.3.0 |

---

## Installed Files

| File | Location |
|------|----------|
| Watson.exe | %ProgramFiles%\Watson\ |
| watson_icon.png | %ProgramFiles%\Watson\ |
| sample_data.csv | %ProgramFiles%\Watson\ |
| README.md | %ProgramFiles%\Watson\Documentation\ |
| LICENSE | %ProgramFiles%\Watson\Documentation\ |
| SECTION_508_COMPLIANCE.md | %ProgramFiles%\Watson\Documentation\ |

---

## Shortcuts Created

| Shortcut | Location |
|----------|----------|
| WATSON | Start Menu\Programs\WATSON\ |
| WATSON | Desktop |

---

## Troubleshooting

### Common Issues

**Installation Fails Silently**
```powershell
# Check MSI log
msiexec /i Watson_1.3.0.msi /l*v install.log
# Review install.log for errors
```

**"Another installation is in progress"**
```powershell
# Wait for other installations or restart Windows Installer service
net stop msiserver
net start msiserver
```

**Access Denied**
- Ensure running as Administrator for per-machine installation
- Check network share permissions for GPO deployment

### Verification Commands

**Check if installed:**
```powershell
Get-WmiObject -Class Win32_Product | Where-Object {$_.Name -like "*WATSON*"}
```

**Check registry:**
```powershell
Get-ItemProperty "HKCU:\Software\AStepInTheRightDirection\Watson"
```

**Check installation path:**
```powershell
Test-Path "${env:ProgramFiles}\Watson\Watson.exe"
```

---

## Support

**Website:** https://www.qualityincourts.com  
**Technical Support:** For enterprise deployment assistance, contact your IT administrator.

---

*Copyright © 2025 A Step in the Right Direction LLC. All Rights Reserved.*
