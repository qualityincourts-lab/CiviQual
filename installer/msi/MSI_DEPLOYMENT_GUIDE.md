# CiviQual Stats MSI Deployment Guide

**Version 1.1.0** | Copyright © 2026 A Step in the Right Direction LLC

---

## Overview

This guide provides instructions for building and deploying CiviQual Stats using Windows Installer (MSI) technology. MSI deployment supports both individual users and enterprise environments:

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

Simply double-click `CiviQualStats_1.2.0.msi` to launch the installation wizard:

1. **Welcome Screen** - Click Next
2. **License Agreement** - Review and accept the license terms
3. **Installation Folder** - Accept default or choose custom location
   - Default: `C:\Program Files\CiviQual`
4. **Ready to Install** - Click Install
5. **Completion** - Click Finish

### Interactive Installation via Command Line

```powershell
msiexec /i CiviQualStats_1.2.0.msi
```

### Modify Installation

To change or repair the installation:
```powershell
msiexec /f CiviQualStats_1.2.0.msi
```

Or use **Settings → Apps → Installed Apps → CiviQual Stats → Modify**

### Uninstall

**Option 1:** Settings → Apps → Installed Apps → CiviQual Stats → Uninstall

**Option 2:** Command line:
```powershell
msiexec /x CiviQualStats_1.2.0.msi
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
4. **CiviQual.exe** built via PyInstaller

### Directory Structure

Prepare the following structure before building:

```
CiviQual_MSI/
├── CiviQual.wxs              # WiX source file (provided)
├── Build-MSI.ps1           # Build script (provided)
├── LICENSE.rtf             # License in RTF format
├── civiqual_icon.ico         # Application icon
└── Files/
    ├── CiviQual.exe          # PyInstaller-built executable
    ├── civiqual_icon.png     # Icon file
    ├── sample_data.csv     # Sample data
    ├── README.md           # Documentation
    ├── LICENSE             # License text
    └── SECTION_508_COMPLIANCE.md
```

### Build Commands

**Using the Build Script (Recommended):**
```powershell
cd CiviQual_MSI
.\Build-MSI.ps1
```

**Manual Build with WiX v4:**
```powershell
wix build CiviQual.wxs -o CiviQualStats_1.2.0.msi -ext WixToolset.UI.wixext
```

**Manual Build with WiX v3 (Legacy):**
```powershell
candle.exe CiviQual.wxs -ext WixUIExtension
light.exe CiviQual.wixobj -ext WixUIExtension -o CiviQualStats_1.2.0.msi
```

---

## Installation Commands

### Interactive Installation
```powershell
msiexec /i CiviQualStats_1.2.0.msi
```

### Silent Installation
```powershell
msiexec /i CiviQualStats_1.2.0.msi /qn
```

### Silent with Logging
```powershell
msiexec /i CiviQualStats_1.2.0.msi /qn /l*v C:\Logs\civiqual_install.log
```

### Custom Installation Path
```powershell
msiexec /i CiviQualStats_1.2.0.msi /qn INSTALLFOLDER="D:\Apps\CiviQual"
```

### Repair Installation
```powershell
msiexec /f CiviQualStats_1.2.0.msi
```

### Silent Uninstall
```powershell
msiexec /x CiviQualStats_1.2.0.msi /qn
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
   \\server\share\Software\CiviQual\CiviQualStats_1.2.0.msi
   ```
   Ensure the share has read permissions for target computers.

2. **Open Group Policy Management Console**
   - Press `Win + R`, type `gpmc.msc`, press Enter

3. **Create or Edit GPO**
   - Right-click the target OU → **Create a GPO in this domain**
   - Name: "CiviQual 1.1.0 Deployment"

4. **Configure Software Installation**
   - Navigate to: `Computer Configuration → Policies → Software Settings → Software Installation`
   - Right-click → **New → Package**
   - Browse to the network share and select `CiviQualStats_1.2.0.msi`
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
3. **Browse** to `CiviQualStats_1.2.0.msi`
4. **Detection Method**: MSI Product Code `{E8F9A1B2-C3D4-5E6F-7A8B-9C0D1E2F3A4B}`

### Deployment Type Settings

| Setting | Value |
|---------|-------|
| Installation Program | `msiexec /i "CiviQualStats_1.2.0.msi" /qn` |
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
3. **Select** the `CiviQualStats_1.2.0.msi` file
4. **Configure App Information**:
   - Name: CiviQual
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
| Product Name | CiviQual |
| Product Version | 1.3.0.0 |
| Product Code | {E8F9A1B2-C3D4-5E6F-7A8B-9C0D1E2F3A4B} |
| Upgrade Code | E8F9A1B2-C3D4-5E6F-7A8B-9C0D1E2F3A4B |
| Manufacturer | A Step in the Right Direction LLC |
| Install Scope | Per-machine |
| Install Location | %ProgramFiles%\CiviQual |

---

## Registry Keys

After installation, the following registry keys are created:

**HKEY_CURRENT_USER\Software\AStepInTheRightDirection\CiviQual**
| Value | Type | Data |
|-------|------|------|
| InstallPath | REG_SZ | [Installation Directory] |
| Version | REG_SZ | 1.3.0 |

---

## Installed Files

| File | Location |
|------|----------|
| CiviQual.exe | %ProgramFiles%\CiviQual\ |
| civiqual_icon.png | %ProgramFiles%\CiviQual\ |
| sample_data.csv | %ProgramFiles%\CiviQual\ |
| README.md | %ProgramFiles%\CiviQual\Documentation\ |
| LICENSE | %ProgramFiles%\CiviQual\Documentation\ |
| SECTION_508_COMPLIANCE.md | %ProgramFiles%\CiviQual\Documentation\ |

---

## Shortcuts Created

| Shortcut | Location |
|----------|----------|
| CiviQual | Start Menu\Programs\CiviQual\ |
| CiviQual | Desktop |

---

## Troubleshooting

### Common Issues

**Installation Fails Silently**
```powershell
# Check MSI log
msiexec /i CiviQualStats_1.2.0.msi /l*v install.log
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
Get-WmiObject -Class Win32_Product | Where-Object {$_.Name -like "*CiviQual*"}
```

**Check registry:**
```powershell
Get-ItemProperty "HKCU:\Software\AStepInTheRightDirection\CiviQual"
```

**Check installation path:**
```powershell
Test-Path "${env:ProgramFiles}\CiviQual\CiviQual.exe"
```

---

## Support

**Website:** https://www.qualityincourts.com  
**Technical Support:** For enterprise deployment assistance, contact your IT administrator.

---

*Copyright © 2026 A Step in the Right Direction LLC. All Rights Reserved.*
