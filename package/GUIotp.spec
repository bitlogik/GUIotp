# -*- mode: python ; coding: utf-8 -*-


import platform
from package.build_win_verinfo import fill_version_info
from gui_otp import VERSION


os_system = platform.system()
if os_system == "Windows":
    os_platform = "win"
elif os_system == "Linux":
    os_platform = "linux"
elif os_system == "Darwin":
    os_platform = "mac"
else:
    raise Exception("Unknown platform target")
plt_arch = platform.machine().lower()

BIN_NAME = "GUIotp" + "-" + os_platform + "-" + plt_arch + "-" + VERSION
FILE_DESCRIPTION = "GUIotp application executable"
COMMENTS = "GUIotp : GUI 2FA OTP desktop app"


pkgs_remove = [
    "sqlite3",
    "_sqlite3",
    "libopenblas",
    "libdgamln",
]

dataset = Analysis(
    ["../gui_otp.py"],
    binaries=[],
    datas=[("../res/guiotp-icon.png", "res/")],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        "curses",
        "pywin.debugger",
        "pywin.debugger.dbgcon",
        "pywin.dialogs",
        "libopenblas",
        "libdgamln",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

for pkg in pkgs_remove:
    dataset.binaries = [x for x in dataset.binaries if not x[0].startswith(pkg)]

pyz = PYZ(dataset.pure, dataset.zipped_data, cipher=None)

if os_platform == "win":
    fill_version_info(BIN_NAME, VERSION, FILE_DESCRIPTION, COMMENTS)
    version_info_file = "version_info"
else:
    version_info_file = None

exe = EXE(
    pyz,
    dataset.scripts,
    dataset.binaries,
    dataset.zipfiles,
    dataset.datas,
    [],
    name=BIN_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    icon="../res/guiotp.ico",
    strip=False,
    upx=False,
    upx_exclude=[],
    console=False,
    version=version_info_file,
)
