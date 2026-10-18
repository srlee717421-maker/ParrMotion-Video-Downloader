; Install the entire PyInstaller folder, including the bundled offline runtimes.
[Setup]
AppId={{91949A39-5B33-4A39-B22F-31C663F24078}
AppName=ParrMotion
AppVersion=1.0.1
AppPublisher=ParrMotion
DefaultDirName={localappdata}\Programs\ParrMotion
DefaultGroupName=ParrMotion
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
SourceDir=..
OutputDir=dist
OutputBaseFilename=ParrMotion-Setup-windows-x64
SetupIconFile=logo.ico
UninstallDisplayIcon={app}\ParrMotion.exe
LicenseFile=LICENSE
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
CloseApplications=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\ParrMotion\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\ParrMotion"; Filename: "{app}\ParrMotion.exe"; WorkingDir: "{app}"
Name: "{autodesktop}\ParrMotion"; Filename: "{app}\ParrMotion.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\ParrMotion.exe"; Description: "{cm:LaunchProgram,ParrMotion}"; Flags: nowait postinstall skipifsilent
