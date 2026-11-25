; Inno Setup script for Heimdall Guardian. Built by tools/build_windows.py, which passes:
;   /DAppVersion=0.0.0        version from pyproject.toml
;   /DSourceDir=<folder>      output of `flet build windows`
;   /DAppExe=<name>.exe       the executable inside SourceDir
;   /DOutputDir=<folder>      where the installer is written (dist/)
;   /DLicenseFile=<file>      the LICENSE file
;   /DIconFile=<file.ico>     optional; without it the default installer icon is used
#ifndef AppVersion
  #error Pass /DAppVersion=<version>
#endif
#ifndef SourceDir
  #error Pass /DSourceDir=<folder with the built app>
#endif
#ifndef AppExe
  #define AppExe "heimdall_guardian.exe"
#endif
#ifndef OutputDir
  #define OutputDir "..\..\dist"
#endif

[Setup]
; Fixed identifier: it is how Windows recognizes upgrades of the same app. Never change it.
AppId={{65F447D0-4ADC-48C8-8999-33CF3FB1CA2E}
AppName=Heimdall Guardian
AppVersion={#AppVersion}
AppPublisher=Alejandro Franco
AppPublisherURL=https://github.com/jafrancov/heimdall-guardian
DefaultDirName={autopf}\Heimdall Guardian
DefaultGroupName=Heimdall Guardian
DisableProgramGroupPage=yes
; Per-user by default (no administrator rights); the dialog lets people choose all users.
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#AppExe}
OutputDir={#OutputDir}
OutputBaseFilename=heimdall-guardian-{#AppVersion}-windows-x64-setup
#ifdef LicenseFile
LicenseFile={#LicenseFile}
#endif
#ifdef IconFile
SetupIconFile={#IconFile}
#endif

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Heimdall Guardian"; Filename: "{app}\{#AppExe}"
Name: "{group}\{cm:UninstallProgram,Heimdall Guardian}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Heimdall Guardian"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "{cm:LaunchProgram,Heimdall Guardian}"; Flags: nowait postinstall skipifsilent
