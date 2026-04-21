# CiviQual Stats v1.2.0 Installation Instructions

**CiviQual Stats** - Statistical Process Control for Public-Sector Quality Management

A statistical analysis tool for Lean Six Sigma practitioners in government and public service.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Quick Start (Run from Source)](#quick-start-run-from-source)
3. [Troubleshooting](#troubleshooting)
4. [Verification](#verification)
5. [Uninstallation](#uninstallation)

---

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| **Operating System** | Windows 10/11, macOS 10.14+, or Linux (Ubuntu 20.04+) |
| **Python** | 3.9 or higher |
| **RAM** | 4 GB minimum, 8 GB recommended |
| **Disk Space** | 500 MB for application + dependencies |
| **Display** | 1280x800 minimum resolution |

### Dependencies

CiviQual Stats requires the following Python packages:

```
PySide6>=6.5.0
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
matplotlib>=3.7.0
openpyxl>=3.1.0
python-docx>=0.8.11
```

CiviQual Stats uses the Arial font, which is pre-installed on all major operating systems.

---

## Quick Start (Run from Source)

### Step 1: Install Python

**Windows:**
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run installer and check "Add Python to PATH"
3. Verify: `python --version`

**macOS:**
```bash
brew install python@3.11
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### Step 2: Extract CiviQual Stats Files

Extract the CiviQualStats_v1.2.0.zip to your preferred location:
- Windows: `C:\CiviQual\CiviQual\`
- macOS/Linux: `~/CiviQualStats/CiviQualStats/`

### Step 3: Install Dependencies

Open a terminal/command prompt in the CiviQualStats folder:

```bash
cd CiviQualStats
pip install -r requirements.txt
```

Or install individually:

```bash
pip install PySide6 pandas numpy scipy matplotlib openpyxl python-docx
```

### Step 4: Run CiviQual Stats

```bash
python main.py
```

**Creating a Desktop Shortcut (Windows):**
1. Right-click on `main.py`
2. Select "Create shortcut"
3. Move shortcut to Desktop
4. Right-click shortcut > Properties > Change Icon > Browse to `civiqual_icon.ico`

**Creating a Desktop Shortcut (macOS/Linux):**
```bash
# Create a shell script
echo '#!/bin/bash
cd ~/CiviQualStats/CiviQualStats
python main.py' > ~/Desktop/CiviQualStats.sh
chmod +x ~/Desktop/CiviQualStats.sh
```

---

## Troubleshooting

### "Python not found" Error

**Windows:**
1. Reinstall Python with "Add Python to PATH" checked
2. Or manually add Python to PATH:
   - Search "Environment Variables"
   - Edit PATH to include Python install directory

**macOS/Linux:**
```bash
# Check if python3 works instead
python3 --version
python3 main.py
```

### "Module not found" Error

Ensure all dependencies are installed:

```bash
pip install --upgrade -r requirements.txt
```

If using Python 3 explicitly:

```bash
pip3 install --upgrade -r requirements.txt
```

### PySide6 Installation Issues

**Windows:**
```bash
pip install --upgrade pip
pip install PySide6
```

**Linux (if Qt dependencies missing):**
```bash
sudo apt install libxcb-xinerama0 libxkbcommon-x11-0
pip install PySide6
```

### matplotlib Font Warnings

If you see font-related warnings, they can typically be ignored. To suppress:

```bash
pip install matplotlib>=3.7.0
```

### High DPI Display Issues

CiviQual Stats supports high DPI displays. If scaling looks incorrect:
1. Right-click CiviQualStats.exe > Properties > Compatibility
2. Click "Change high DPI settings"
3. Check "Override high DPI scaling behavior"
4. Select "Application" from dropdown

---

## Verification

After installation, verify CiviQual Stats is working correctly:

1. Launch CiviQual Stats
2. Click **File > Open Sample Data**
3. Select any column with numeric data
4. Click **Generate 4-Up Chart** on the Measure tab
5. Verify the chart displays with correct colors:
   - Blue data points
   - Burgundy title
   - Teal control limits

---

## Uninstallation

### Source Installation

Simply delete the CiviQualStats folder. No registry entries are created when running from source.

---

## Support

**Documentation**: See included README.md and SECTION_508_COMPLIANCE.md

**License**: Free for government and nonprofit use. See LICENSE file.

**Contact**: www.qualityincourts.com

---

*"CiviQual" and "CiviQual Stats" are trademarks of A Step in the Right Direction LLC.*

© 2026 A Step in the Right Direction LLC
