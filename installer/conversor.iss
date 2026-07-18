; Script de Inno Setup para Conversor de Archivos
; Genera el instalador para Windows

#define MyAppName "Conversor de Archivos"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "John"
#define MyAppURL "https://github.com/John54571/Conversor-de-Archivos"
#define MyAppExeName "ConversorDeArchivos.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={localappdata}\ConversorDeArchivos
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=
OutputDir=..\dist
OutputBaseFilename=ConversorDeArchivos-Setup
SetupIconFile=..\conversor\assets\iconochoro.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "installffmpeg"; Description: "Instalar FFmpeg (requerido para audio/video)"; GroupDescription: "Componentes adicionales:"; Flags: unchecked

[Files]
Source: "..\dist\ConversorDeArchivos.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\conversor\assets\iconochoro.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\iconochoro.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\iconochoro.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Función para registrar el menú contextual de Windows
procedure RegisterContextMenu();
var
  RegKey: string;
begin
  RegKey := '*\shell\ConversorDeArchivos';
  RegWriteStringValue(HKEY_CLASSES_ROOT, RegKey, '', 'Convertir con Conversor de Archivos');
  RegWriteStringValue(HKEY_CLASSES_ROOT, RegKey, 'Icon', ExpandConstant('{app}\iconochoro.ico'));
  RegWriteStringValue(HKEY_CLASSES_ROOT, RegKey + '\command', '', '"' + ExpandConstant('{app}\{#MyAppExeName}') + '" "%1"');
end;

// Función para desregistrar el menú contextual
procedure UnregisterContextMenu();
begin
  RegDeleteKeyIncludingSubkeys(HKEY_CLASSES_ROOT, '*\shell\ConversorDeArchivos\command');
  RegDeleteKeyIfEmpty(HKEY_CLASSES_ROOT, '*\shell\ConversorDeArchivos');
end;

// Descargar e instalar FFmpeg
procedure InstallFFmpeg();
var
  FFmpegDir: string;
  FFmpegExe: string;
begin
  FFmpegDir := ExpandConstant('{app}\ffmpeg\bin');
  FFmpegExe := FFmpegDir + '\ffmpeg.exe';
  
  if not FileExists(FFmpegExe) then
  begin
    // Nota: En un instalador real, aquí se descargaría FFmpeg
    // Por ahora, solo creamos el directorio
    ForceDirectories(FFmpegDir);
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Registrar menú contextual
    RegisterContextMenu();
    
    // Instalar FFmpeg si el usuario lo seleccionó
    if WizardIsTaskSelected('installffmpeg') then
    begin
      InstallFFmpeg();
    end;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usUninstall then
  begin
    // Desregistrar menú contextual al desinstalar
    UnregisterContextMenu();
  end;
end;
