@echo off
REM =====================================================
REM CiviQual Stats MSI Build Script (WiX v4 Required)
REM Copyright (c) 2026 A Step in the Right Direction LLC
REM =====================================================
REM
REM Prerequisites:
REM   1. Python 3.9+ with pip
REM   2. .NET SDK 6.0+
REM   3. WiX v4: dotnet tool install --global wix
REM   4. WiX UI: wix extension add WixToolset.UI.wixext
REM
REM Usage:
REM   cd installer\msi
REM   Build-MSI.bat
REM
REM =====================================================

setlocal enabledelayedexpansion

set VERSION=1.2.0
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..\..
set OUTPUT_FILE=CiviQualStats_%VERSION%.msi

echo.
echo =====================================================
echo   CiviQual Stats MSI Build Script
echo   Version: %VERSION%
echo =====================================================
echo.

REM =====================================================
REM Check Prerequisites
REM =====================================================
echo [1/6] Checking prerequisites...

REM Check Python
where python >nul 2>&1
if errorlevel 1 (
    echo   ERROR: Python not found. Install Python 3.9+ and add to PATH.
    goto :error
)
echo   [OK] Python found

REM Check WiX v4
where wix >nul 2>&1
if errorlevel 1 (
    echo.
    echo   ERROR: WiX Toolset v4 not found.
    echo.
    echo   Install WiX v4:
    echo     1. Install .NET SDK from https://dotnet.microsoft.com/download
    echo     2. Run: dotnet tool install --global wix
    echo     3. Run: wix extension add WixToolset.UI.wixext
    echo     4. Restart this command prompt
    echo.
    goto :error
)
echo   [OK] WiX v4 found

REM Check WiX UI extension
wix extension list 2>&1 | findstr /i "WixToolset.UI.wixext" >nul
if errorlevel 1 (
    echo   Installing WixToolset.UI.wixext...
    wix extension add WixToolset.UI.wixext
    if errorlevel 1 (
        echo   ERROR: Failed to install UI extension.
        echo   Run manually: wix extension add WixToolset.UI.wixext
        goto :error
    )
)
echo   [OK] WiX UI extension

REM Check PyInstaller
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo   Installing PyInstaller...
    pip install pyinstaller
)
echo   [OK] PyInstaller

REM Check Pillow
pip show pillow >nul 2>&1
if errorlevel 1 (
    echo   Installing Pillow...
    pip install pillow
)
echo   [OK] Pillow
echo.

REM =====================================================
REM Generate Icon
REM =====================================================
echo [2/6] Generating application icon...
cd /d "%PROJECT_ROOT%"
python create_icon.py
if not exist "civiqual_icon.ico" (
    echo   ERROR: Failed to create civiqual_icon.ico
    goto :error
)
echo   [OK] Icon created
echo.

REM =====================================================
REM Install Dependencies
REM =====================================================
echo [3/6] Installing Python dependencies...
pip install -r requirements.txt -q
echo   [OK] Dependencies installed
echo.

REM =====================================================
REM Build Executable
REM =====================================================
echo [4/6] Building CiviQualStats.exe with PyInstaller...
echo   This takes 2-5 minutes...

cd /d "%PROJECT_ROOT%"
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

pyinstaller --name CiviQualStats --onefile --windowed --icon=civiqual_icon.ico --add-data "samples;samples" --noconfirm main.py

if not exist "dist\CiviQualStats.exe" (
    echo   ERROR: PyInstaller failed to create CiviQualStats.exe
    goto :error
)
echo   [OK] CiviQualStats.exe created
echo.

REM =====================================================
REM Prepare Files
REM =====================================================
echo [5/6] Preparing MSI files...
cd /d "%SCRIPT_DIR%"

if exist "Files" rmdir /s /q "Files"
mkdir "Files"
mkdir "Files\samples"

copy "%PROJECT_ROOT%\dist\CiviQualStats.exe" "Files\" >nul
copy "%PROJECT_ROOT%\civiqual_icon.png" "Files\" >nul
copy "%PROJECT_ROOT%\civiqual_icon.ico" "Files\" >nul
copy "%PROJECT_ROOT%\README.md" "Files\" >nul
copy "%PROJECT_ROOT%\LICENSE" "Files\" >nul
copy "%PROJECT_ROOT%\SECTION_508_COMPLIANCE.md" "Files\" >nul
copy "%PROJECT_ROOT%\samples\*.csv" "Files\samples\" >nul
copy "%PROJECT_ROOT%\civiqual_icon.ico" "." >nul

echo   [OK] Files prepared
echo.

REM =====================================================
REM Build MSI
REM =====================================================
echo [6/6] Building MSI with WiX...
echo.

echo   Verifying Files\ directory contents:
dir Files\ /b
echo.
echo   Verifying Files\samples\ directory contents:
dir Files\samples\ /b
echo.

echo   Running: wix build CiviQual.wxs -o %OUTPUT_FILE% -ext WixToolset.UI.wixext
echo.

wix build CiviQual.wxs -o "%OUTPUT_FILE%" -ext WixToolset.UI.wixext 2>&1

if errorlevel 1 (
    echo.
    echo   ===============================================
    echo   ERROR: WiX build failed. See error above.
    echo   ===============================================
    echo.
    echo   Common fixes:
    echo     1. wix extension add WixToolset.UI.wixext
    echo     2. Ensure all source files exist in Files\
    echo     3. Check CiviQual.wxs XML syntax
    echo.
    goto :error
)

if not exist "%OUTPUT_FILE%" (
    echo   ERROR: MSI file was not created.
    goto :error
)

for %%A in ("%OUTPUT_FILE%") do set SIZE=%%~zA
set /a SIZE_MB=%SIZE%/1048576

echo.
echo =====================================================
echo   BUILD SUCCESSFUL
echo =====================================================
echo.
echo   Output: %CD%\%OUTPUT_FILE%
echo   Size:   %SIZE_MB% MB
echo.
echo   Install:   msiexec /i %OUTPUT_FILE%
echo   Silent:    msiexec /i %OUTPUT_FILE% /qn
echo   Uninstall: msiexec /x %OUTPUT_FILE% /qn
echo.
echo =====================================================

goto :done

:error
echo.
echo BUILD FAILED - See errors above.
echo.
pause
exit /b 1

:done
pause
exit /b 0
