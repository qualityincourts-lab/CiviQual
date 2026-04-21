@echo off
REM =========================================================================
REM CiviQual Stats v2.0.0 — Build script
REM
REM Builds per-user and per-machine MSI installers and signs them.
REM Requires:
REM   - WiX v5 toolset (wix.exe on PATH)
REM   - signtool.exe from the Windows SDK
REM   - Certum code-signing certificate installed in the user store
REM =========================================================================

setlocal EnableDelayedExpansion

set VERSION=2.0.0
set THUMBPRINT=E6830B627AF1AD8980FADDF221D27FAE361A166D
set TIMESTAMP=http://time.certum.pl
set SIGNTOOL="C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe"

echo.
echo === CiviQual Stats v%VERSION% build ===
echo.

REM --- Per-user MSI --------------------------------------------------------
echo [1/4] Building per-user MSI...
wix build CiviQualStats.wxs -d Scope=perUser -o CiviQualStats_%VERSION%_PerUser.msi
if errorlevel 1 (
    echo ERROR: Per-user build failed.
    exit /b 1
)

REM --- Per-machine MSI -----------------------------------------------------
echo [2/4] Building per-machine MSI...
wix build CiviQualStats.wxs -d Scope=perMachine -o CiviQualStats_%VERSION%_PerMachine.msi
if errorlevel 1 (
    echo ERROR: Per-machine build failed.
    exit /b 1
)

REM --- Sign both MSIs ------------------------------------------------------
echo [3/4] Signing per-user MSI...
%SIGNTOOL% sign /sha1 %THUMBPRINT% /fd SHA256 /tr %TIMESTAMP% /td SHA256 /d "CiviQual Stats %VERSION%" CiviQualStats_%VERSION%_PerUser.msi
if errorlevel 1 (
    echo ERROR: Signing per-user MSI failed.
    exit /b 1
)

echo [4/4] Signing per-machine MSI...
%SIGNTOOL% sign /sha1 %THUMBPRINT% /fd SHA256 /tr %TIMESTAMP% /td SHA256 /d "CiviQual Stats %VERSION%" CiviQualStats_%VERSION%_PerMachine.msi
if errorlevel 1 (
    echo ERROR: Signing per-machine MSI failed.
    exit /b 1
)

echo.
echo === Build complete ===
echo   - CiviQualStats_%VERSION%_PerUser.msi
echo   - CiviQualStats_%VERSION%_PerMachine.msi
echo.
endlocal
