; CiviQual Stats Installer Script for Inno Setup
; Version 1.2.0 - CiviQual Stats Pro Release
; Copyright (c) 2026 A Step in the Right Direction LLC
; All Rights Reserved.
;
; This script creates a professional Windows installer for CiviQual Stats
; Download Inno Setup from: https://jrsoftware.org/isinfo.php

#define MyAppName "CiviQual Stats"
#define MyAppVersion "1.2.0"
#define MyAppPublisher "A Step in the Right Direction LLC"
#define MyAppURL "https://www.qualityincourts.com"
#define MyAppExeName "CiviQualStats.exe"
#define MyAppDescription "Statistical Process Control for Public-Sector Quality Management"

[Setup]
; Application information
AppId={{E8F9A1B2-C3D4-5E6F-7A8B-9C0D1E2F3A4B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppCopyright=Copyright (c) 2026 A Step in the Right Direction LLC

; Installation directories
DefaultDirName={autopf}\CiviQual Stats
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; License agreement - REQUIRED
LicenseFile=LICENSE.rtf

; Output settings
OutputDir=output
OutputBaseFilename=CiviQualStats_Setup_{#MyAppVersion}
SetupIconFile=..\civiqual_icon.ico
UninstallDisplayIcon={app}\CiviQualStats.exe

; Compression
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes

; Windows version requirements
MinVersion=10.0
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Privileges
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Installer appearance
WizardStyle=modern
WizardSizePercent=100

; Info before/after install
InfoBeforeFile=InfoBefore.txt

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main application (PyInstaller output - entire folder)
Source: "..\dist\CiviQualStats\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Icon files (may already be in dist, but ensure they are present)
Source: "..\civiqual_icon.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\civiqual_icon.ico"; DestDir: "{app}"; Flags: ignoreversion

; Documentation
Source: "..\CiviQualStats_User_Guide.docx"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\SECTION_508_COMPLIANCE.md"; DestDir: "{app}"; Flags: ignoreversion

; Sample data files (may already be in dist via --add-data, but ensure present)
Source: "..\samples\sample_data.csv"; DestDir: "{app}\samples"; Flags: ignoreversion
Source: "..\samples\sample_311_services.csv"; DestDir: "{app}\samples"; Flags: ignoreversion
Source: "..\samples\sample_benefits.csv"; DestDir: "{app}\samples"; Flags: ignoreversion
Source: "..\samples\sample_citizen_services.csv"; DestDir: "{app}\samples"; Flags: ignoreversion
Source: "..\samples\sample_court_cases.csv"; DestDir: "{app}\samples"; Flags: ignoreversion
Source: "..\samples\sample_court_clerk.csv"; DestDir: "{app}\samples"; Flags: ignoreversion
Source: "..\samples\sample_inspections.csv"; DestDir: "{app}\samples"; Flags: ignoreversion
Source: "..\samples\sample_mail_processing.csv"; DestDir: "{app}\samples"; Flags: ignoreversion
Source: "..\samples\sample_permits.csv"; DestDir: "{app}\samples"; Flags: ignoreversion
Source: "..\samples\sample_public_health.csv"; DestDir: "{app}\samples"; Flags: ignoreversion
Source: "..\samples\sample_public_records.csv"; DestDir: "{app}\samples"; Flags: ignoreversion

[Icons]
; Start Menu shortcuts
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Comment: "{#MyAppDescription}"
Name: "{group}\Sample Data"; Filename: "{app}\samples"
Name: "{group}\Section 508 Compliance"; Filename: "{app}\SECTION_508_COMPLIANCE.md"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop shortcut (optional)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; Comment: "{#MyAppDescription}"

; Quick launch (legacy)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Option to launch after install
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
; Application registration
Root: HKLM; Subkey: "Software\A Step in the Right Direction LLC\CiviQualStats"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\A Step in the Right Direction LLC\CiviQualStats"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"

[UninstallDelete]
; Clean up configuration files on uninstall (optional - user data)
Type: filesandordirs; Name: "{localappdata}\CiviQualStats"

[Code]
// Custom initialization code
function InitializeSetup(): Boolean;
begin
  Result := True;
  // Add any custom checks here (e.g., .NET Framework version)
end;

// Custom messages
procedure InitializeWizard();
begin
  WizardForm.WelcomeLabel2.Caption := 
    'This will install CiviQual Stats (Statistical Process Control for Public-Sector Quality Management) on your computer.' + #13#10 + #13#10 +
    'CiviQual Stats is the first product in the CiviQual Suite family of quality management tools, designed for Lean Six Sigma practitioners in government and public service organizations.' + #13#10 + #13#10 +
    'The Free Tier includes Yellow Belt and basic Green Belt statistical tools for basic SPC and data analysis. CiviQual Stats Pro (paid license) adds advanced Green Belt and Black Belt tools.' + #13#10 + #13#10 +
    'Click Next to continue, or Cancel to exit Setup.';
end;
