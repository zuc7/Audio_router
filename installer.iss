#define AppName "Audio Router"
#define AppVersion GetEnv("APP_VERSION")
#define AppVersionInfo GetEnv("APP_VERSION_INFO")
#define AppExeName "audio_router_gui.exe"
#define AppPublisher "zuc7"

[Setup]
AppId={{F3D7B2E6-7B83-4A0D-9F6E-7A0F0E9A9E73}}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppCopyright=Copyright (C) 2026 {#AppPublisher}
AppComments=Route audio for Windows apps with a clean Windows installer.
LicenseFile=LICENSE
VersionInfoVersion={#AppVersionInfo}
VersionInfoTextVersion={#AppVersion}
DefaultDirName={autopf}\Audio Router
DefaultGroupName=Audio Router
OutputDir=release
OutputBaseFilename=AudioRouter-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupIconFile=app.ico
UninstallDisplayIcon={app}\{#AppExeName}

[Files]
Source: "dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "app.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Audio Router"; Filename: "{app}\{#AppExeName}"
Name: "{commondesktop}\Audio Router"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch Audio Router"; Flags: nowait postinstall skipifsilent
