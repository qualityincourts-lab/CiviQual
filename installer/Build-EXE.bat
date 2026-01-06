@echo off
REM =====================================================
REM WATSON EXE Installer Build Script
REM Copyright (c) 2025 A Step in the Right Direction LLC
REM =====================================================
REM
REM This script builds the complete Watson EXE installer
REM from source using Inno Setup.
REM
REM Prerequisites:
REM   1. Python 3.9+ with pip
REM   2. Inno Setup 6.x installed
REM   3. All Watson source files in parent directory
REM
REM Usage:
REM   Build-EXE.bat
REM
REM =====================================================

setlocal enabledelayedexpansion

REM Configuration
set VERSION=1.3.0
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

echo.
echo =====================================================
echo   WATSON EXE Installer Build Script
echo   Version: %VERSION%
echo =====================================================
echo.

REM =====================================================
REM Step 1: Check Prerequisites
REM =====================================================
echo [Step 1/5] Checking prerequisites...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python 3.9+ and add to PATH
    goto :error
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
echo   [OK] Python %PYTHON_VER%

REM Check Inno Setup
set ISCC_PATH=
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
) else if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=%ProgramFiles%\Inno Setup 6\ISCC.exe"
) else (
    REM Try PATH
    where iscc >nul 2>&1
    if not errorlevel 1 (
        set ISCC_PATH=iscc
    )
)

if "%ISCC_PATH%"=="" (
    echo ERROR: Inno Setup not found
    echo.
    echo Please install Inno Setup 6 from:
    echo   https://jrsoftware.org/isinfo.php
    echo.
    goto :error
)
echo   [OK] Inno Setup found

REM Check PyInstaller
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo   [  ] PyInstaller not installed - installing...
    pip install pyinstaller
    if errorlevel 1 goto :error
)
echo   [OK] PyInstaller

REM Check Pillow
pip show pillow >nul 2>&1
if errorlevel 1 (
    echo   [  ] Pillow not installed - installing...
    pip install pillow
    if errorlevel 1 goto :error
)
echo   [OK] Pillow

echo.

REM =====================================================
REM Step 2: Generate Application Icon
REM =====================================================
echo [Step 2/5] Generating application icon...

cd /d "%PROJECT_ROOT%"
if not exist "create_icon.py" (
    echo ERROR: create_icon.py not found in %PROJECT_ROOT%
    goto :error
)

python create_icon.py
if errorlevel 1 (
    echo ERROR: Icon generation failed
    goto :error
)

if not exist "watson_icon.ico" (
    echo ERROR: watson_icon.ico was not created
    goto :error
)
echo   [OK] watson_icon.ico created
echo.

REM =====================================================
REM Step 3: Install Dependencies
REM =====================================================
echo [Step 3/5] Installing Python dependencies...

pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo WARNING: Some dependencies may have failed to install
)
echo   [OK] Dependencies installed
echo.

REM =====================================================
REM Step 4: Build Executable with PyInstaller
REM =====================================================
echo [Step 4/5] Building executable with PyInstaller...
echo   This may take several minutes...

cd /d "%PROJECT_ROOT%"

REM Clean previous builds
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "Watson.spec" del "Watson.spec"

REM Build executable
pyinstaller --name Watson --windowed --icon=watson_icon.ico ^
    --add-data "samples;samples" ^
    --noconfirm ^
    main.py

if errorlevel 1 (
    echo ERROR: PyInstaller build failed
    goto :error
)

if not exist "dist\Watson\Watson.exe" (
    echo ERROR: Watson.exe was not created
    goto :error
)
echo   [OK] Watson.exe built successfully
echo.

REM =====================================================
REM Step 5: Build EXE Installer with Inno Setup
REM =====================================================
echo [Step 5/5] Building EXE installer with Inno Setup...

cd /d "%SCRIPT_DIR%"

REM Create Output directory if it does not exist
if not exist "Output" mkdir "Output"

REM Compile the installer
"%ISCC_PATH%" Watson_Setup.iss
if errorlevel 1 (
    echo ERROR: Inno Setup compilation failed
    goto :error
)

set OUTPUT_FILE=Output\Watson_Setup_%VERSION%.exe
if not exist "%OUTPUT_FILE%" (
    REM Try alternate naming
    set OUTPUT_FILE=Output\Watson_Setup_1.3.0.exe
)

if not exist "%OUTPUT_FILE%" (
    echo ERROR: Installer was not created
    goto :error
)

REM Get file size
for %%A in (%OUTPUT_FILE%) do set EXE_SIZE=%%~zA
set /a EXE_SIZE_MB=%EXE_SIZE% / 1048576

echo.
echo =====================================================
echo   BUILD SUCCESSFUL!
echo =====================================================
echo.
echo   Output:   %SCRIPT_DIR%%OUTPUT_FILE%
echo   Size:     ~%EXE_SIZE_MB% MB
echo.
echo   The installer will:
echo     - Install Watson to Program Files
echo     - Create Start Menu shortcuts
echo     - Create desktop shortcut (optional)
echo     - Register uninstaller
echo.
echo   Silent installation:
echo     Watson_Setup_%VERSION%.exe /VERYSILENT /NORESTART
echo.
echo =====================================================
goto :end

:error
echo.
echo =====================================================
echo   BUILD FAILED
echo =====================================================
echo.
echo   Please check the error messages above.
echo   Common issues:
echo     - Python not in PATH
echo     - Inno Setup not installed
echo     - Missing source files
echo     - Insufficient disk space
echo.
exit /b 1

:end
endlocal
exit /b 0
