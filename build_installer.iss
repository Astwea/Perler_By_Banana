; ========== 拼豆图案生成系统 - 安装程序（中英双语）==========
; 编译命令: iscc build_installer.iss

[Setup]
; 基本信息
AppId={{5A5E5A5E-5E5E-5E5E-5E5A5E5A5E5E}
AppName=拼豆图案生成系统 / Perler Pattern Generator System
AppVersion=1.0.0
AppVerName=拼豆图案生成系统 v1.0.0 / Perler Pattern Generator System v1.0.0
AppPublisher=PerlerByBanana
AppPublisherURL=https://github.com/Astwea/Perler_By_Banana
AppSupportURL=https://github.com/Astwea/Perler_By_Banana/issues
AppUpdatesURL=https://github.com/Astwea/Perler_By_Banana/releases

; 默认安装目录
DefaultDirName={autopf}\拼豆图案生成系统
DefaultGroupName=拼豆图案生成系统

; 输出设置
OutputDir=installer
OutputBaseFilename=拼豆图案生成系统_v1.0.0_安装程序_Setup
Compression=none  ; 不压缩（用户要求）
SolidCompression=no

; 安装程序设置
SetupIconFile=desktop\resources\icons\app_icon.ico
WizardStyle=modern
WindowVisible=yes
WindowShowCaption=yes
WindowResizable=yes
MinVersion=6.1sp1
PrivilegesRequired=admin
AllowNoIcons=yes
UsePreviousAppDir=yes
UsePreviousGroup=yes
UninstallDisplayIcon={app}\拼豆图案生成系统.exe
AppMutex=PerlerPatternGeneratorMutex

; 许可协议
LicenseFile=LICENSE

; 多语言支持
Languages:
    Name: "chinesesimp"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
    Name: "english"; MessagesFile: "compiler:Languages\English.isl"

[Tasks]
; 安装任务
Name: "desktopicon"; Description: "创建桌面快捷方式 / Create Desktop Shortcut"; GroupDescription: "附加图标 / Additional Icons:"
Name: "quicklaunchicon"; Description: "创建快速启动图标 / Create Quick Launch Icon"; GroupDescription: "附加图标 / Additional Icons:"
Name: "associate"; Description: "关联图片文件 / Associate Image Files"; GroupDescription: "文件关联 / File Association:"; Flags: unchecked

[Files]
; 复制程序文件
Source: "dist\拼豆图案生成系统\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
; 创建用户项目空间
Name: "{userprofile}\PerlerByBanana\workspace"; Flags: uninsneveruninstall
Name: "{userprofile}\PerlerByBanana\workspace\output"; Flags: uninsneveruninstall
Name: "{userprofile}\PerlerByBanana\workspace\images"; Flags: uninsneveruninstall
Name: "{userprofile}\PerlerByBanana\workspace\logs"; Flags: uninsneveruninstall
Name: "{userprofile}\PerlerByBanana\workspace\user_data"; Flags: uninsneveruninstall

[Icons]
; 开始菜单快捷方式（中文）
Name: "{group}\拼豆图案生成系统"; Filename: "{app}\拼豆图案生成系统.exe"; IconFilename: "{app}\app_icon.ico"; Languages: chinesesimp
Name: "{group}\卸载拼豆图案生成系统"; Filename: "{uninstallexe}"; Languages: chinesesimp

; 开始菜单快捷方式（英文）
Name: "{group}\Perler Pattern Generator System"; Filename: "{app}\拼豆图案生成系统.exe"; IconFilename: "{app}\app_icon.ico"; Languages: english
Name: "{group}\Uninstall Perler Pattern Generator System"; Filename: "{uninstallexe}"; Languages: english

; 桌面快捷方式
Name: "{commondesktop}\拼豆图案生成系统"; Filename: "{app}\拼豆图案生成系统.exe"; IconFilename: "{app}\app_icon.ico"; Tasks: desktopicon

; 快速启动
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\拼豆图案生成系统"; Filename: "{app}\拼豆图案生成系统.exe"; Tasks: quicklaunchicon

[Registry]
; 文件关联
Root: HKCR; Subkey: ".png"; ValueType: string; ValueName: "PerlerApp"; ValueData: "PNG Image"; Flags: uninsdeletevalue; Tasks: associate
Root: HKCR; Subkey: ".jpg"; ValueType: string; ValueName: "PerlerApp"; ValueData: "JPEG Image"; Flags: uninsdeletevalue; Tasks: associate
Root: HKCR; Subkey: ".jpeg"; ValueType: string; ValueName: "PerlerApp"; ValueData: "JPEG Image"; Flags: uninsdeletevalue; Tasks: associate
Root: HKCR; Subkey: ".bmp"; ValueType: string; ValueName: "PerlerApp"; ValueData: "Bitmap Image"; Flags: uninsdeletevalue; Tasks: associate
Root: HKCR; Subkey: "PerlerApp"; ValueType: string; ValueName: ""; ValueData: "拼豆图案生成系统 / Perler Pattern Generator System"; Flags: uninsdeletekey; Tasks: associate
Root: HKCR; Subkey: "PerlerApp\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\app_icon.ico,0"; Flags: uninsdeletekey; Tasks: associate
Root: HKCR; Subkey: "PerlerApp\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\拼豆图案生成系统.exe"" ""%1"""; Flags: uninsdeletekey; Tasks: associate

[Run]
; 安装后运行
Filename: "{app}\拼豆图案生成系统.exe"; Description: "启动拼豆图案生成系统 / Launch Application"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; 卸载时只删除日志，保留用户数据
Type: filesandordirs; Name: "{app}\logs"

[Code]
// 自定义页面和逻辑

procedure CurPageChanged(CurPageID: Integer);
var
  LangStr: String;
begin
  // 根据语言设置文本
  if ActiveLanguage = 'chinesesimp' then
    LangStr := 'zh'
  else
    LangStr := 'en';

  // 欢迎页面
  if CurPageID = wpWelcome then
  begin
    if LangStr = 'zh' then
    begin
      WizardForm.WelcomeLabel1.Caption := '欢迎使用 拼豆图案生成系统 安装向导';
      WizardForm.WelcomeLabel2.Caption := '本程序将在您的计算机上安装 拼豆图案生成系统。'#13#10#13#10'点击"下一步"继续。';
    end
    else
    begin
      WizardForm.WelcomeLabel1.Caption := 'Welcome to Perler Pattern Generator System Setup Wizard';
      WizardForm.WelcomeLabel2.Caption := 'This will install Perler Pattern Generator System on your computer.'#13#10#13#10'Click Next to continue.';
    end;
  end;

  // 许可协议页面
  if CurPageID = wpLicense then
  begin
    if LangStr = 'zh' then
    begin
      WizardForm.LicenseAcceptedRadio.Caption := '我同意许可协议';
      WizardForm.LicenseNotAcceptedRadio.Caption := '我不同意许可协议';
    end
    else
    begin
      WizardForm.LicenseAcceptedRadio.Caption := 'I accept the license agreement';
      WizardForm.LicenseNotAcceptedRadio.Caption := 'I do not accept the license agreement';
    end;
  end;

  // 选择目录页面
  if CurPageID = wpSelectDir then
  begin
    if LangStr = 'zh' then
    begin
      WizardForm.SelectDirLabel.Caption := '选择安装程序将安装文件的文件夹：';
      WizardForm.SelectDirBrowseLabel.Caption := '点击"浏览..."选择不同的文件夹。';
      WizardForm.DirEditLabel.Caption := '目标文件夹：';
    end
    else
    begin
      WizardForm.SelectDirLabel.Caption := 'Select of folder where you would like to install the program files:';
      WizardForm.SelectDirBrowseLabel.Caption := 'Click "Browse..." to choose a different folder.';
      WizardForm.DirEditLabel.Caption := 'Destination folder:';
    end;
  end;

  // 安装进度页面
  if CurPageID = wpInstalling then
  begin
    if LangStr = 'zh' then
    begin
      WizardForm.StatusLabel.Caption := '正在安装 拼豆图案生成系统...';
      WizardForm.FilenameLabel.Caption := '正在解压文件...';
    end
    else
    begin
      WizardForm.StatusLabel.Caption := 'Installing Perler Pattern Generator System...';
      WizardForm.FilenameLabel.Caption := 'Extracting files...';
    end;
  end;

  // 完成页面
  if CurPageID = wpFinished then
  begin
    if LangStr = 'zh' then
    begin
      WizardForm.FinishedLabel.Caption := '拼豆图案生成系统 已成功安装到您的计算机。'#13#10#13#10'点击"完成"退出安装向导。';
      WizardForm.RunList.Items.Text := '启动拼豆图案生成系统';
    end
    else
    begin
      WizardForm.FinishedLabel.Caption := 'Perler Pattern Generator System has been successfully installed on your computer.'#13#10#13#10'Click Finish to exit the Setup Wizard.';
      WizardForm.RunList.Items.Text := 'Launch Perler Pattern Generator System';
    end;
  end;
end;

// 自定义背景
procedure InitializeWizard();
begin
  WizardForm.Color := clBtnFace;
  WizardForm.TitleColor := $004A90E2;  // 浅蓝色
end;

// 检查是否正在运行
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;

  // 检查程序是否正在运行
  if CheckForMutexes('PerlerPatternGeneratorMutex') then
  begin
    if ActiveLanguage = 'chinesesimp' then
      Result := MsgBox('检测到 拼豆图案生成系统 正在运行，请先关闭程序后再继续安装。'#13#10#13#10'是否继续安装？',
        mbConfirmation, MB_YESNO) = IDYES
    else
      Result := MsgBox('Perler Pattern Generator System is currently running. Please close the program before continuing.'#13#10#13#10'Continue with installation?',
        mbConfirmation, MB_YESNO) = IDYES;
  end;
end;

// 卸载前检查
function InitializeUninstall(): Boolean;
begin
  Result := True;

  if CheckForMutexes('PerlerPatternGeneratorMutex') then
  begin
    if ActiveLanguage = 'chinesesimp' then
      MsgBox('检测到 拼豆图案生成系统 正在运行，请先关闭程序。', mbError, MB_OK)
    else
      MsgBox('Perler Pattern Generator System is currently running. Please close the program.', mbError, MB_OK);

    Result := False;
  end;
end;
