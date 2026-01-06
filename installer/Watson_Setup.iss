; WATSON Installer Script for Inno Setup
; Version 1.3.0 - Section 508 Accessibility Release
; Copyright (c) 2025 A Step in the Right Direction LLC
; All Rights Reserved.
;
; This script creates a professional Windows installer for WATSON
; Download Inno Setup from: https://jrsoftware.org/isinfo.php

#define MyAppName "WATSON"
#define MyAppVersion "1.3.0"
#define MyAppPublisher "A Step in the Right Direction LLC"
#define MyAppURL "https://www.qualityincourts.com"
#define MyAppExeName "Watson.exe"
#define MyAppDescription "Workbench for Analysis, Testing, Statistics, Optimization & Navigation"

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
AppCopyright=Copyright (c) 2025 A Step in the Right Direction LLC

; Installation directories
DefaultDirName={autopf}\Watson
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; License agreement - REQUIRED
LicenseFile=LICENSE.rtf

; Output settings
OutputDir=output
OutputBaseFilename=Watson_Setup_{#MyAppVersion}
SetupIconFile=..\watson_icon.ico
UninstallDisplayIcon={app}\Watson.exe

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
Source: "..\dist\Watson\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Icon files (may already be in dist, but ensure they are present)
Source: "..\watson_icon.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\watson_icon.ico"; DestDir: "{app}"; Flags: ignoreversion

; Documentation
Source: "..\WATSON_User_Guide.docx"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
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
Root: HKLM; Subkey: "Software\A Step in the Right Direction LLC\WATSON"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\A Step in the Right Direction LLC\WATSON"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"

[UninstallDelete]
; Clean up configuration files on uninstall (optional - user data)
Type: filesandordirs; Name: "{localappdata}\WATSON"

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
    'This will install WATSON (Workbench for Analysis, Testing, Statistics, Optimization & Navigation) on your computer.' + #13#10 + #13#10 +
    'WATSON is a statistical analysis tool designed for Lean Six Sigma practitioners in service industries, including public sector organizations.' + #13#10 + #13#10 +
    'Version 1.3.0 includes Section 508 accessibility improvements for users with disabilities.' + #13#10 + #13#10 +
    'This software is FREE for government agencies and nonprofit organizations. Commercial use requires a separate license from A Step in the Right Direction LLC.' + #13#10 + #13#10 +
    'Click Next to continue, or Cancel to exit Setup.';
end;
