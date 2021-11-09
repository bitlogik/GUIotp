;----  GUIotp Windows installer script ----
; Copyright (C) 2021 BitLogiK

!addplugindir nsis_plugins
!addincludedir nsis_plugins
!include "WordFunc.nsh"
!include "FileFunc.nsh"

; Script version; displayed when running the installer
!define INSTALLER_VERSION "1.0"

; Detect version from file
!searchparse /file ../gui_otp.py `VERSION = "` PROGRAM_VERSION `"`
!ifndef PROGRAM_VERSION
   !error "Program Version Undefined"
!endif

; program information
!define PROGRAM_NAME "GUIotp"
!define PROGRAM_EXE "GUIotp-win-amd64-${PROGRAM_VERSION}.exe"
!define PROGRAM_WEB_SITE "https://github.com/bitlogik/GUIotp"
!define APPGUID "078de467-4199-45e7-a6a8-01273e6d92ad"

!define BUILD_DIR "..\dist"
!define INSTALLER_FILENAME "GUIotp-${PROGRAM_VERSION}-setup.exe"

; Set default compressor
SetCompressor /FINAL /SOLID lzma
SetCompressorDictSize 32

; --- Interface settings ---
; Modern User Interface 2
!include "MUI2.nsh"
; Installer
!define MUI_ICON "../res/guiotp.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_RIGHT
; !define MUI_HEADERIMAGE_BITMAP "installer-top.bmp"
; !define MUI_WELCOMEFINISHPAGE_BITMAP "installer-side.bmp"
!define MUI_COMPONENTSPAGE_SMALLDESC
!define MUI_ABORTWARNING
; Start Menu Folder Page Configuration
!define MUI_STARTMENUPAGE_DEFAULTFOLDER ${PROGRAM_NAME}
!define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKCR"
!define MUI_STARTMENUPAGE_REGISTRY_KEY "Software\${PROGRAM_NAME}"
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"
; Uninstaller
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"
; !define MUI_HEADERIMAGE_UNBITMAP "installer-top.bmp"
; !define MUI_WELCOMEFINISHPAGE_UNBITMAP "installer-side.bmp"
!define MUI_UNFINISHPAGE_NOAUTOCLOSE
; Add shortcut
!define MUI_FINISHPAGE_SHOWREADME ""
!define MUI_FINISHPAGE_SHOWREADME_TEXT "Create Desktop Shortcut"
!define MUI_FINISHPAGE_SHOWREADME_FUNCTION CreateDesktopShortcut

; --- Start of Modern User Interface ---

; Welcome
!insertmacro MUI_PAGE_WELCOME

; Run installation
!insertmacro MUI_PAGE_INSTFILES
; Popup Message if VC Redist missing
; Page Custom VCRedistMessage
; Display 'finished' page
!insertmacro MUI_PAGE_FINISH
; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES
; Language files
!insertmacro MUI_LANGUAGE "English"


; --- Functions ---

Function checkGuiotpRunning
    check:
        System::Call 'kernel32::OpenMutex(i 0x100000, b 0, t "GUIotp*") i .R0'
        IntCmp $R0 0 notRunning
            System::Call 'kernel32::CloseHandle(i $R0)'
            MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION \
                "GUIotp is running, please close it first.$\n$\n \
                Click `OK` to retry or `Cancel` to cancel this upgrade." \
                /SD IDCANCEL IDOK check
            Abort
    notRunning:
FunctionEnd

; Check for running GUIotp instance.
Function .onInit

    UserInfo::GetAccountType
    pop $0
    ${If} $0 != "admin" ;Require admin rights on NT4+
        MessageBox mb_iconstop "Administrator rights are required for the installation."
        SetErrorLevel 740 ;ERROR_ELEVATION_REQUIRED
        Quit
    ${EndIf}

    Call checkGuiotpRunning

FunctionEnd

Function un.onUninstSuccess
    HideWindow
    MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) was successfully removed from your computer." /SD IDOK
FunctionEnd

Function un.onInit
    checkUn:
        System::Call 'kernel32::OpenMutex(i 0x100000, b 0, t "GUIotp*") i .R0'
        IntCmp $R0 0 notRunningUn
            System::Call 'kernel32::CloseHandle(i $R0)'
            MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION \
                "GUIotp is running, please close it first.$\n$\n \
                Click `OK` to retry or `Cancel` to cancel this uninstallation." \
                /SD IDCANCEL IDOK checkUn
            Abort
    notRunningUn:
        MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to remove $(^Name)?" /SD IDYES IDYES +2
        Abort
FunctionEnd

Function CreateDesktopShortcut
    CreateShortCut "$DESKTOP\GUIotp.lnk" "$INSTDIR\${PROGRAM_EXE}"
FunctionEnd

; --- Installation sections ---
!define PROGRAM_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\{${APPGUID}}"
!define PROGRAM_UNINST_ROOT_KEY "HKLM"
!define PROGRAM_UNINST_FILENAME "$INSTDIR\GUIotp-uninst.exe"

BrandingText "${PROGRAM_NAME} Windows Installer v${INSTALLER_VERSION}"
Name "${PROGRAM_NAME} ${PROGRAM_VERSION}"
OutFile "${BUILD_DIR}\${INSTALLER_FILENAME}"
InstallDir "$PROGRAMFILES64\GUIotp"

; No need for such details
ShowInstDetails hide
ShowUnInstDetails hide

; Check 64 bits
!include "LogicLib.nsh"
!include "x64.nsh"
Section
${IfNot} ${RunningX64}
    MessageBox mb_iconstop "Sorry, this requires a 64 bits Windows."
    SetErrorLevel 1637 ;ERROR_INSTALL_PLATFORM_UNSUPPORTED
    Quit
${EndIf}
SectionEnd

; Install main application
Section "GUIotp : 2FA TOTP GUI client for desktop" Section1
    SectionIn RO
    
    SetOverwrite ifnewer
    SetOutPath "$INSTDIR"
    WriteIniStr "$INSTDIR\homepage.url" "InternetShortcut" "URL" "${PROGRAM_WEB_SITE}"
    File "${BUILD_DIR}\${PROGRAM_EXE}"
    File "..\res\guiotp.ico"

    SetShellVarContext all
    CreateDirectory "$SMPROGRAMS\GUIotp"
    CreateShortCut "$SMPROGRAMS\GUIotp\GUIotp.lnk" "$INSTDIR\${PROGRAM_EXE}"
    CreateShortCut "$SMPROGRAMS\GUIotp\GUIotp Website.lnk" "$INSTDIR\homepage.url"
    CreateShortCut "$SMPROGRAMS\GUIotp\Uninstall GUIotp.lnk" ${PROGRAM_UNINST_FILENAME}
    SetShellVarContext current
    WriteRegStr HKCU "Software\${PROGRAM_NAME}" "" $INSTDIR
SectionEnd

; Create uninstaller.
Section -Uninstaller
    WriteUninstaller ${PROGRAM_UNINST_FILENAME}
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD ${PROGRAM_UNINST_ROOT_KEY} "${PROGRAM_UNINST_KEY}" "EstimatedSize" "$0"
    WriteRegStr ${PROGRAM_UNINST_ROOT_KEY} "${PROGRAM_UNINST_KEY}" "DisplayName" ${PROGRAM_NAME}
    WriteRegStr ${PROGRAM_UNINST_ROOT_KEY} "${PROGRAM_UNINST_KEY}" "UninstallString" ${PROGRAM_UNINST_FILENAME}
    WriteRegStr ${PROGRAM_UNINST_ROOT_KEY} "${PROGRAM_UNINST_KEY}" "DisplayVersion" ${PROGRAM_VERSION}
    WriteRegStr ${PROGRAM_UNINST_ROOT_KEY} "${PROGRAM_UNINST_KEY}" "Publisher" "BitLogiK"
    WriteRegStr ${PROGRAM_UNINST_ROOT_KEY} "${PROGRAM_UNINST_KEY}" "DisplayIcon" "$INSTDIR\res\guiotp.ico"
SectionEnd

; --- Uninstallation section ---
Section Uninstall
    ; Delete GUIotp files.
    Delete "$INSTDIR\homepage.url"
    Delete ${PROGRAM_UNINST_FILENAME}
    RmDir "$INSTDIR"

    ; Delete Start Menu items.
    SetShellVarContext all
    Delete "$SMPROGRAMS\GUIotp\GUIotp.lnk"
    Delete "$SMPROGRAMS\GUIotp\Uninstall GUIotp.lnk"
    Delete "$SMPROGRAMS\GUIotp\GUIotp Website.lnk"
    RmDir "$SMPROGRAMS\GUIotp"
    DeleteRegKey /ifempty HKCR "Software\GUIotp"
    SetShellVarContext current
    Delete "$DESKTOP\GUIotp.lnk"

    ; Delete registry keys.
    DeleteRegKey ${PROGRAM_UNINST_ROOT_KEY} "${PROGRAM_UNINST_KEY}"

  ; Explorer shortcut keys potentially set by the application's settings
  DeleteRegKey HKCU "Software\Classes\CLSID\{${APPGUID}}"
  DeleteRegKey HKCU "Software\Classes\Wow6432Node\CLSID\{${APPGUID}"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Explorer\Desktop\NameSpace\{${APPGUID}"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Explorer\HideDesktopIcons\NewStartPanel\{${APPGUID}"

SectionEnd

; Add version info to installer properties.
VIProductVersion "${INSTALLER_VERSION}.0.0"
VIAddVersionKey ProductName ${PROGRAM_NAME}
VIAddVersionKey Comments "GUIotp : 2FA OTP app"
VIAddVersionKey CompanyName "BitLogiK"
VIAddVersionKey LegalCopyright "BitLogiK"
VIAddVersionKey FileDescription "${PROGRAM_NAME} Application Installer"
VIAddVersionKey FileVersion "${INSTALLER_VERSION}.0.0"
VIAddVersionKey ProductVersion "${PROGRAM_VERSION}.0"
VIAddVersionKey OriginalFilename ${INSTALLER_FILENAME}

ManifestDPIAware true
