@echo off
REM ==========================================
REM WATSON MSI Code Signing Script
REM Using Certum Standard Code Signing in the Cloud
REM 
REM Prerequisites:
REM 1. Certum certificate activated and issued
REM 2. SimplySign Desktop installed
REM 3. SimplySign mobile app installed
REM 4. Windows SDK installed (for SignTool)
REM ==========================================

echo.
echo ==========================================
echo    WATSON MSI Code Signing
echo    Certum Cloud Certificate
echo ==========================================
echo.
echo BEFORE RUNNING THIS SCRIPT:
echo.
echo 1. Open SimplySign Desktop application
echo 2. Open SimplySign app on your phone
echo 3. Generate a 6-digit token in the mobile app
echo 4. Enter the token in SimplySign Desktop
echo 5. Wait for "Connected" status
echo.
echo ==========================================
echo.
pause

REM === Configuration ===
REM Update CERT_NAME to match your certificate exactly
set CERT_NAME=A Step in the Right Direction LLC

REM SignTool location (update version number if different)
set SIGNTOOL="C:\Program Files (x86)\Windows Kits\10\bin\10.0.17763.0\x64\signtool.exe"

REM If the above path does not work, try finding SignTool:
REM where /r "C:\Program Files (x86)\Windows Kits" signtool.exe

REM Timestamp server (Certum)
set TIMESTAMP=http://time.certum.pl

REM Backup timestamp servers if Certum is unavailable:
REM http://timestamp.sectigo.com
REM http://timestamp.digicert.com
REM http://timestamp.globalsign.com/tsa/r6advanced1

REM MSI file to sign
set MSI_FILE=Watson_1.3.0.msi

REM === Check if MSI exists ===
if not exist "%MSI_FILE%" (
    echo.
    echo ERROR: %MSI_FILE% not found!
    echo.
    echo Please run Build-MSI.bat first to create the installer.
    echo.
    pause
    exit /b 1
)

REM === Check if SignTool exists ===
if not exist %SIGNTOOL% (
    echo.
    echo ERROR: SignTool not found at:
    echo %SIGNTOOL%
    echo.
    echo Please install Windows SDK or update the path in this script.
    echo Download from: https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/
    echo.
    pause
    exit /b 1
)

REM === Sign the MSI ===
echo.
echo Signing %MSI_FILE%...
echo.
echo Certificate: %CERT_NAME%
echo Timestamp:   %TIMESTAMP%
echo.

%SIGNTOOL% sign /n "%CERT_NAME%" /tr %TIMESTAMP% /td sha256 /fd sha256 /v "%MSI_FILE%"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ==========================================
    echo ERROR: Signing failed!
    echo ==========================================
    echo.
    echo Common causes:
    echo - SimplySign Desktop not connected
    echo - Token expired (generate a new one)
    echo - Certificate name does not match
    echo - Certificate not yet issued
    echo.
    echo To debug, run:
    echo %SIGNTOOL% sign /debug /n "%CERT_NAME%" /fd sha256 "%MSI_FILE%"
    echo.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo SUCCESS: MSI signed successfully!
echo ==========================================
echo.

REM === Verify the signature ===
echo Verifying signature...
echo.

%SIGNTOOL% verify /pa /v "%MSI_FILE%"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: Signature verification returned an error.
    echo The file may still be signed - check Properties ^> Digital Signatures
    echo.
) else (
    echo.
    echo Signature verified successfully!
    echo.
)

REM === Display signature info ===
echo.
echo ==========================================
echo To view the signature:
echo 1. Right-click %MSI_FILE%
echo 2. Click Properties
echo 3. Click Digital Signatures tab
echo ==========================================
echo.

pause
